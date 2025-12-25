from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
import csv
import threading
from datetime import datetime

app = FastAPI(title="Snack POS API")

# ให้ React เรียก API ได้ (รองรับทั้ง localhost และ 127.0.0.1)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = Path(__file__).parent
PRODUCTS_FILE = DATA_DIR / "snacks.csv"
SALES_FILE = DATA_DIR / "sales.csv"
MEMBERS_FILE = DATA_DIR / "member.csv"

lock = threading.Lock()


# =========================
# Products
# =========================
def read_products():
    if not PRODUCTS_FILE.exists():
        PRODUCTS_FILE.write_text("barcode,name,price,stock\n", encoding="utf-8")

    with PRODUCTS_FILE.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    out = []
    for r in rows:
        out.append(
            {
                "barcode": str(r.get("barcode", "")).strip(),
                "name": str(r.get("name", "")).strip(),
                "price": float(r.get("price", 0) or 0),
                "stock": int(r.get("stock", 0) or 0),
            }
        )
    return out


def save_products(rows):
    with PRODUCTS_FILE.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["barcode", "name", "price", "stock"])
        writer.writeheader()
        for r in rows:
            writer.writerow(
                {
                    "barcode": r["barcode"],
                    "name": r["name"],
                    "price": r["price"],
                    "stock": r["stock"],
                }
            )


# =========================
# Members
# =========================
def _ensure_member_headers(path: Path):
    """
    รองรับไฟล์ member.csv 2 แบบ:
    1) มี header: id,display,group
    2) ไม่มี header และมี 3 คอลัมน์: id,display,group
    ถ้าไม่มี header จะพยายามอ่านแบบไม่มี header แล้ว map ให้เอง
    """
    # ไม่ทำอะไร ถ้าไม่มีไฟล์
    if not path.exists():
        return


def read_members():
    """
    อ่าน member.csv แล้วคืนเป็น list ของ:
    { id, display, group, label }

    label จะเป็นรูปแบบ: "Boss 1D"
    """
    if not MEMBERS_FILE.exists():
        return []

    _ensure_member_headers(MEMBERS_FILE)

    # ลองอ่านแบบมี header ก่อน
    with MEMBERS_FILE.open("r", newline="", encoding="utf-8-sig") as f:
        sample = f.read(2048)
        f.seek(0)

        # เช็กว่ามี header "id" ไหม
        has_header = "id" in sample.splitlines()[0].lower() and "display" in sample.splitlines()[0].lower()

        members = []

        if has_header:
            reader = csv.DictReader(f)
            for r in reader:
                mid = str(r.get("id", "")).strip()
                display = str(r.get("display", "")).strip() or mid
                group = str(r.get("group", "")).strip() or "Unknown"

                if not (mid or display):
                    continue

                label = f"{display} {group}".strip()
                members.append(
                    {"id": mid or display, "display": display, "group": group, "label": label}
                )
        else:
            # ไม่มี header: อ่านแบบ row ธรรมดา (3 คอลัมน์)
            reader = csv.reader(f)
            for row in reader:
                if not row or len(row) < 1:
                    continue

                # รองรับ: id, display, group
                mid = str(row[0]).strip() if len(row) >= 1 else ""
                display = str(row[1]).strip() if len(row) >= 2 else mid
                group = str(row[2]).strip() if len(row) >= 3 else "Unknown"

                if not (mid or display):
                    continue

                label = f"{display} {group}".strip()
                members.append(
                    {"id": mid or display, "display": display, "group": group, "label": label}
                )

    # sort ตาม group แล้วตาม display
    members.sort(key=lambda x: (x["group"], x["display"].lower()))
    return members


# =========================
# Sales
# =========================
def append_sale(operator, total, items, after_stock_map):
    if not SALES_FILE.exists():
        with SALES_FILE.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "operator", "total", "items", "remaining"])

    ts = datetime.now().strftime("%d/%m/%Y %H:%M")
    items_str = " | ".join([f"{it['name']} x{it['qty']}" for it in items])
    remain_str = ", ".join([f"{name}={stk}" for name, stk in after_stock_map.items()])

    with SALES_FILE.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([ts, operator, total, items_str, remain_str])


# =========================
# API Endpoints
# =========================
@app.get("/products")
def get_products():
    return read_products()


@app.get("/members")
def get_members():
    return read_members()


class CartItem(BaseModel):
    barcode: str
    qty: int


class CheckoutReq(BaseModel):
    operator: str = "unknown"
    items: list[CartItem]


@app.post("/checkout")
def checkout(req: CheckoutReq):
    if not req.items:
        raise HTTPException(400, "No items")

    with lock:
        rows = read_products()
        by_bc = {r["barcode"]: r for r in rows}

        total = 0.0
        items_detail = []

        # ตรวจ + คำนวณราคารวม
        for it in req.items:
            bc = it.barcode.strip()
            if bc not in by_bc:
                raise HTTPException(404, f"Not found {bc}")
            r = by_bc[bc]
            if r["stock"] < it.qty:
                raise HTTPException(400, f"Stock not enough: {r['name']}")
            total += float(r["price"]) * it.qty
            items_detail.append(
                {"barcode": bc, "name": r["name"], "price": r["price"], "qty": it.qty}
            )

        # หักสต็อก
        after_stock_map = {}
        for it in req.items:
            r = by_bc[it.barcode.strip()]
            r["stock"] = int(r["stock"]) - it.qty
            after_stock_map[r["name"]] = r["stock"]

        save_products(rows)

        # บันทึกการขายลง sales.csv
        append_sale(req.operator, total, items_detail, after_stock_map)

    return {"message": "ok", "total": total}
