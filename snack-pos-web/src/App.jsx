import { useEffect, useMemo, useState } from "react";

const API = "http://127.0.0.1:8000";

export default function App() {
  /* ================= state ================= */
  const [products, setProducts] = useState([]);
  const [members, setMembers] = useState([]);

  const [operator, setOperator] = useState("");
  const [cart, setCart] = useState({});
  const [select, setSelect] = useState("");
  const [qty, setQty] = useState(1);

  const [showPopup, setShowPopup] = useState(false);
  const [isFinishing, setIsFinishing] = useState(false);

  /* ================= คำนวณยอด ================= */
  const total = useMemo(() => {
    return Object.values(cart).reduce((sum, i) => sum + i.qty * i.price, 0);
  }, [cart]);

  /* ================= โหลดสินค้า ================= */
  const loadProducts = () => {
    fetch(`${API}/products`)
      .then((r) => r.json())
      .then((d) => {
        const arr = Array.isArray(d) ? d : [];
        setProducts(arr);
        if (arr.length && !select) setSelect(arr[0].barcode);
      })
      .catch(() => {
        alert("โหลดสินค้าไม่ได้");
        setProducts([]);
      });
  };

  /* ================= โหลดสมาชิก ================= */
  const loadMembers = () => {
    fetch(`${API}/members`)
      .then((r) => r.json())
      .then((d) => {
        const arr = Array.isArray(d) ? d : [];
        setMembers(arr);
        if (arr.length && !operator) {
          setOperator(arr[0].label); // default ตัวแรก
        }
      })
      .catch(() => {
        setMembers([]);
        if (!operator) setOperator("unknown");
      });
  };

  useEffect(() => {
    loadProducts();
    loadMembers();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  /* ================= cart ================= */
  function add() {
    if (!select) return;
    const p = products.find((x) => x.barcode === select);
    if (!p) return;

    const q = Math.max(1, Number(qty) || 1);
    const cur = cart[p.barcode]?.qty || 0;

    if (cur + q > p.stock) {
      alert("สินค้าในคลังไม่พอ");
      return;
    }

    setCart({
      ...cart,
      [p.barcode]: { ...p, qty: cur + q },
    });
  }

  function removeItem(barcode) {
    const next = { ...cart };
    delete next[barcode];
    setCart(next);
  }

  /* ================= popup ================= */
  function confirm() {
    if (Object.keys(cart).length === 0) {
      alert("ยังไม่มีสินค้า");
      return;
    }
    setShowPopup(true);
  }

  function closePopup() {
    if (!isFinishing) setShowPopup(false);
  }

  function finish() {
    const items = Object.values(cart).map((i) => ({
      barcode: i.barcode,
      qty: i.qty,
    }));

    if (items.length === 0) return;

    setIsFinishing(true);

    fetch(`${API}/checkout`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ operator, items }),
    })
      .then((r) => r.json().then((data) => ({ ok: r.ok, data })))
      .then(({ ok, data }) => {
        if (!ok) {
          alert(`ผิดพลาด: ${data?.detail || "error"}`);
          return;
        }
        alert(`เสร็จสิ้น ✅ รวม ${data.total} บาท`);
        setCart({});
        setShowPopup(false);
        loadProducts();
      })
      .catch(() => alert("เชื่อมต่อ backend ไม่ได้"))
      .finally(() => setIsFinishing(false));
  }

  /* ================= group members ================= */
  const groupedMembers = useMemo(() => {
    const map = new Map();
    for (const m of members) {
      const g = m.group || "Unknown";
      if (!map.has(g)) map.set(g, []);
      map.get(g).push(m);
    }
    return Array.from(map.entries());
  }, [members]);

  /* ================= UI ================= */
  return (
    <div style={{ padding: 20, fontFamily: "sans-serif" }}>
      <h2>Snack POS</h2>

      {/* ===== คนทำรายการ ===== */}
      <div style={{ marginBottom: 12 }}>
        คนทำรายการ:{" "}
        {members.length > 0 ? (
          <select value={operator} onChange={(e) => setOperator(e.target.value)}>
            {groupedMembers.map(([group, list]) => (
              <optgroup key={group} label={group}>
                {list.map((m) => (
                  <option key={m.id} value={m.label}>
                    {m.label}
                  </option>
                ))}
              </optgroup>
            ))}
          </select>
        ) : (
          <input value={operator} onChange={(e) => setOperator(e.target.value)} />
        )}
      </div>

      {/* ===== เลือกสินค้า ===== */}
      <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
        <select value={select} onChange={(e) => setSelect(e.target.value)}>
          {products.length === 0 ? (
            <option disabled>กำลังโหลด...</option>
          ) : (
            products.map((p) => (
              <option key={p.barcode} value={p.barcode}>
                {p.name} ({p.price}฿) - คงเหลือ {p.stock}
              </option>
            ))
          )}
        </select>

        <input
          type="number"
          min="1"
          value={qty}
          onChange={(e) => setQty(e.target.value)}
          style={{ width: 80 }}
        />

        <button onClick={add}>เพิ่ม</button>
      </div>

      <hr />

      {/* ===== ตะกร้า ===== */}
      <h3>ตะกร้า</h3>
      {Object.values(cart).length === 0 ? (
        <div>ยังไม่มีสินค้า</div>
      ) : (
        Object.values(cart).map((i) => (
          <div key={i.barcode}>
            {i.name} x {i.qty} = {i.qty * i.price} บาท{" "}
            <button onClick={() => removeItem(i.barcode)}>ลบ</button>
          </div>
        ))
      )}

      <h3>รวม: {total} บาท</h3>
      <button onClick={confirm}>ยืนยัน</button>

      {/* ===== popup ===== */}
      {showPopup && (
        <div
          onClick={closePopup}
          style={{
            position: "fixed",
            inset: 0,
            background: "rgba(0,0,0,0.45)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <div
            onClick={(e) => e.stopPropagation()}
            style={{
              position: "relative",
              background: "white",
              borderRadius: 12,
              padding: 20,
              width: 360,
              textAlign: "center",
            }}
          >
            <button
              onClick={closePopup}
              disabled={isFinishing}
              style={{
                position: "absolute",
                top: 8,
                right: 8,
                border: "none",
                background: "transparent",
                fontSize: 20,
              }}
            >
              ✕
            </button>

            <h3>กรุณาสแกน QR</h3>

            <img
              src="/qr.png"
              alt="QR"
              style={{ width: "100%", maxWidth: 260 }}
            />

            <div style={{ marginTop: 10 }}>
              ยอดชำระ: <b>{total}</b> บาท
            </div>

            <button
              onClick={finish}
              disabled={isFinishing}
              style={{
                marginTop: 14,
                padding: "8px 18px",
                background: "#4caf50",
                color: "white",
                border: "none",
                borderRadius: 6,
              }}
            >
              {isFinishing ? "กำลังบันทึก..." : "เสร็จสิ้น"}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
