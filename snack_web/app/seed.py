import csv
from pathlib import Path
from datetime import datetime

from app.core.database import SessionLocal
from app.modules.users.models import Member
from app.modules.snacks.models import Snack
from app.modules.stock.models import Stock
from app.modules.sales.models import Sale


ROOT = Path(__file__).parent.parent
MEMBERS_FILE = ROOT / "member.csv"
SNACKS_FILE = ROOT / "snacks.csv"
SALES_FILE = ROOT / "sales.csv"
STOCK_FILE = ROOT / "stock.csv"


def seed_members(session):
    if not MEMBERS_FILE.exists():
        print("No member.csv found — skipping members")
        return 0

    count = 0
    with MEMBERS_FILE.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            mid = (r.get("id") or "").strip()
            display = (r.get("display") or "").strip() or mid
            group = (r.get("group") or "").strip() or "Unknown"
            if not (mid or display):
                continue
            m = Member(id=mid or display, name=display, member_class=group)
            session.merge(m)
            count += 1
    return count


def seed_snacks(session):
    if not SNACKS_FILE.exists():
        print("No snacks.csv found — skipping snacks")
        return 0

    count = 0
    with SNACKS_FILE.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            barcode = (r.get("barcode") or "").strip()
            if not barcode:
                continue
            name = (r.get("name") or "").strip()
            price = float(r.get("price") or 0)
            s = Snack(barcode=barcode, name=name, price=price)
            session.merge(s)
            count += 1
    return count


def parse_timestamp(s: str):
    s = (s or "").strip()
    if not s:
        return None
    # try common formats
    for fmt in ("%d/%m/%Y %H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(s, fmt)
        except Exception:
            continue
    return None


def seed_stock(session):
    if not STOCK_FILE.exists():
        print("No stock.csv found — skipping stock")
        return 0

    count = 0
    with STOCK_FILE.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            sid = (r.get("id") or "").strip()
            create_at = parse_timestamp(r.get("create_at"))
            snack_id = (r.get("snack_id") or "").strip()
            snack_id = snack_id or None
            quantity = int(float(r.get("quantity") or 0))
            quantity_now = int(float(r.get("quantity_now") or 0))
            st = Stock(id=sid or None, create_at=create_at, snack_id=snack_id, quantity=quantity, quantity_now=quantity_now)
            session.merge(st)
            count += 1
    return count


def seed_sales(session):
    if not SALES_FILE.exists():
        print("No sales.csv found — skipping sales")
        return 0

    count = 0
    with SALES_FILE.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            sid = (r.get("id") or "").strip()
            ts = parse_timestamp(r.get("timestamp"))
            snack_id = (r.get("snack_id") or "").strip()
            quantity = int(float(r.get("quantity") or 0))

            sale = Sale(
                id=sid or None,
                timestamp=ts,
                snack_id=snack_id,
                quantity=quantity,
            )
            session.merge(sale)
            count += 1
    return count


def run():
    session = SessionLocal()
    try:
        m = seed_members(session)
        s = seed_snacks(session)
        st = seed_stock(session)
        sa = seed_sales(session)
        session.commit()
        print(f"Seeded: members={m}, snacks={s}, stock={st}, sales={sa}")
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    run()
