from datetime import datetime, timezone
from flask import current_app
from app.db import get_db

DEFAULT_STATIONS = [
    ("PS5-01","PS5","console",100),("PS5-02","PS5","console",100),
    ("PS5-03","PS5","console",100),("PS5-04","PS5","console",100),
    ("PS4-01","PS4","console",100),("PS4-02","PS4","console",100),
    ("POOL-01","Pool","table",200),("POOL-02","Pool","table",200),
    ("TT-01","Tennis","table",200),("TT-02","Tennis","table",200)
]
DEFAULT_PRODUCTS = [
    ("COKE-01","Coca Cola","Drinks",60,30,5),
    ("PEPSI-01","Pepsi","Drinks",60,30,5),
    ("WATER-01","Mineral Water","Drinks",30,50,10),
    ("CHIPS-01","Potato Chips","Snacks",40,25,5),
    ("MAGGI-01","Masala Maggi","Food",70,20,5),
    ("COFFEE-01","Cold Coffee","Drinks",90,15,3),
    ("ENERGY-01","Energy Drink","Drinks",120,12,3),
    ("BROWNIE-01","Chocolate Brownie","Food",100,10,2)
]

def now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def row_dict(row):
    return dict(row) if row else None

def seed_database(force=False):
    db = get_db()
    if force:
        for s in DEFAULT_STATIONS:
            db.execute("INSERT OR REPLACE INTO stations(id,type,group_name,rate,status) VALUES(?,?,?,?, 'available')", s)
        for p in DEFAULT_PRODUCTS:
            db.execute("""INSERT OR REPLACE INTO products(sku,name,category,price,stock,low_stock)
                          VALUES(?,?,?,?,?,?)""", p)
    else:
        if db.execute("SELECT COUNT(*) c FROM stations").fetchone()["c"] == 0:
            for s in DEFAULT_STATIONS:
                db.execute("INSERT INTO stations(id,type,group_name,rate,status) VALUES(?,?,?,?, 'available')", s)
        if db.execute("SELECT COUNT(*) c FROM products").fetchone()["c"] == 0:
            for p in DEFAULT_PRODUCTS:
                db.execute("""INSERT INTO products(sku,name,category,price,stock,low_stock)
                              VALUES(?,?,?,?,?,?)""", p)
    db.commit()

def station_config():
    db = get_db()
    return [dict(r) for r in db.execute("""
        SELECT s.*, 
          (SELECT COUNT(*) FROM sessions x WHERE x.station_id=s.id AND x.status='active') active_count
        FROM stations s ORDER BY s.id
    """)]

def update_station_rate(station_id, data):
    rate = float(data.get("rate", 0))
    if rate <= 0:
        raise ValueError("Rate must be greater than zero.")
    db = get_db()
    cur = db.execute("UPDATE stations SET rate=? WHERE id=?", (rate, station_id))
    if cur.rowcount == 0:
        raise ValueError("Station not found.")
    db.commit()
    return row_dict(db.execute("SELECT * FROM stations WHERE id=?", (station_id,)).fetchone())

def create_session(data):
    station_id = data.get("station_id")
    name = (data.get("customer_name") or "").strip()
    phone = (data.get("phone") or "").strip()
    if not station_id or not name:
        raise ValueError("Station and customer name are required.")
    db = get_db()
    station = db.execute("SELECT * FROM stations WHERE id=?", (station_id,)).fetchone()
    if not station:
        raise ValueError("Station not found.")
    if db.execute("SELECT 1 FROM sessions WHERE station_id=? AND status='active'", (station_id,)).fetchone():
        raise ValueError("Station is already active.")
    started = now()
    cur = db.execute("""INSERT INTO sessions(station_id,customer_name,phone,started_at,rate,status)
                        VALUES(?,?,?,?,?,'active')""",
                     (station_id,name,phone,started,station["rate"]))
    if phone:
        db.execute("""INSERT INTO customers(name,phone,visits,total_spent)
                      VALUES(?,?,0,0)
                      ON CONFLICT(phone) DO UPDATE SET name=excluded.name""", (name,phone))
    db.commit()
    return row_dict(db.execute("SELECT * FROM sessions WHERE id=?", (cur.lastrowid,)).fetchone())

def stop_session(session_id, data):
    db = get_db()
    s = db.execute("SELECT * FROM sessions WHERE id=? AND status='active'", (session_id,)).fetchone()
    if not s:
        raise ValueError("Active session not found.")
    ended = now()
    start = datetime.fromisoformat(s["started_at"])
    end = datetime.fromisoformat(ended)
    mins = max(1, int((end-start).total_seconds()/60 + 0.999))
    total = round((mins/60)*s["rate"], 2)
    payment = data.get("payment_method") or "Cash"
    db.execute("""UPDATE sessions SET ended_at=?, duration_minutes=?, total=?, payment_method=?, status='completed'
                  WHERE id=?""", (ended,mins,total,payment,session_id))
    if s["phone"]:
        db.execute("""INSERT INTO customers(name,phone,visits,total_spent)
                      VALUES(?,?,1,?)
                      ON CONFLICT(phone) DO UPDATE SET
                      name=excluded.name, visits=customers.visits+1,
                      total_spent=customers.total_spent+excluded.total_spent""",
                   (s["customer_name"],s["phone"],total))
    db.commit()
    return row_dict(db.execute("SELECT * FROM sessions WHERE id=?", (session_id,)).fetchone())

def list_sessions():
    db = get_db()
    return [dict(r) for r in db.execute("""
        SELECT * FROM sessions ORDER BY id DESC
    """)]

def list_products():
    db = get_db()
    return [dict(r) for r in db.execute("SELECT * FROM products WHERE active=1 ORDER BY category,name")]

def create_product(data):
    name=(data.get("name") or "").strip()
    sku=(data.get("sku") or "").strip().upper()
    category=(data.get("category") or "Other").strip()
    price=float(data.get("price",0))
    stock=int(data.get("stock",0))
    low=int(data.get("low_stock",5))
    if not name or not sku or price < 0 or stock < 0:
        raise ValueError("Valid SKU, name, price and stock are required.")
    db=get_db()
    try:
        cur=db.execute("""INSERT INTO products(sku,name,category,price,stock,low_stock)
                          VALUES(?,?,?,?,?,?)""",(sku,name,category,price,stock,low))
        db.commit()
    except Exception as e:
        raise ValueError("SKU already exists.") from e
    return row_dict(db.execute("SELECT * FROM products WHERE id=?",(cur.lastrowid,)).fetchone())

def update_product(product_id,data):
    db=get_db()
    p=db.execute("SELECT * FROM products WHERE id=?",(product_id,)).fetchone()
    if not p: raise ValueError("Product not found.")
    price=float(data.get("price",p["price"]))
    stock=int(data.get("stock",p["stock"]))
    name=data.get("name",p["name"])
    db.execute("UPDATE products SET name=?,price=?,stock=? WHERE id=?",(name,price,stock,product_id))
    db.commit()
    return row_dict(db.execute("SELECT * FROM products WHERE id=?",(product_id,)).fetchone())

def create_sale(data):
    items=data.get("items") or []
    if not items: raise ValueError("Cart is empty.")
    db=get_db()
    subtotal=0
    normalized=[]
    for item in items:
        pid=int(item["product_id"]); qty=int(item["quantity"])
        p=db.execute("SELECT * FROM products WHERE id=? AND active=1",(pid,)).fetchone()
        if not p: raise ValueError("Product not found.")
        if qty <= 0 or p["stock"] < qty: raise ValueError(f"Insufficient stock for {p['name']}.")
        total=p["price"]*qty
        subtotal+=total
        normalized.append((p,qty,total))
    discount=float(data.get("discount",0))
    tax=float(data.get("tax",0))
    total=max(0,round(subtotal-discount+tax,2))
    payment=data.get("payment_method") or "Cash"
    cur=db.execute("""INSERT INTO sales(customer_name,phone,subtotal,discount,tax,total,payment_method)
                      VALUES(?,?,?,?,?,?,?)""",
                   (data.get("customer_name"),data.get("phone"),subtotal,discount,tax,total,payment))
    sale_id=cur.lastrowid
    for p,qty,line in normalized:
        db.execute("""INSERT INTO sale_items(sale_id,product_id,quantity,unit_price,total)
                      VALUES(?,?,?,?,?)""",(sale_id,p["id"],qty,p["price"],line))
        db.execute("UPDATE products SET stock=stock-? WHERE id=?",(qty,p["id"]))
    if data.get("phone"):
        db.execute("""INSERT INTO customers(name,phone,visits,total_spent)
                      VALUES(?,?,1,?)
                      ON CONFLICT(phone) DO UPDATE SET
                      name=excluded.name, visits=customers.visits+1,
                      total_spent=customers.total_spent+excluded.total_spent""",
                   (data.get("customer_name") or "Guest",data["phone"],total))
    db.commit()
    return row_dict(db.execute("SELECT * FROM sales WHERE id=?",(sale_id,)).fetchone())

def list_sales():
    db=get_db()
    sales=[]
    for r in db.execute("SELECT * FROM sales ORDER BY id DESC"):
        sale=dict(r)
        sale["items"]=[dict(x) for x in db.execute("""
            SELECT si.*,p.name,p.sku FROM sale_items si JOIN products p ON p.id=si.product_id
            WHERE si.sale_id=?""",(r["id"],))]
        sales.append(sale)
    return sales

def add_expense(data):
    category=(data.get("category") or "Other").strip()
    description=(data.get("description") or "").strip()
    amount=float(data.get("amount",0))
    if not description or amount<=0: raise ValueError("Description and positive amount required.")
    db=get_db()
    cur=db.execute("INSERT INTO expenses(category,description,amount) VALUES(?,?,?)",(category,description,amount))
    db.commit()
    return row_dict(db.execute("SELECT * FROM expenses WHERE id=?",(cur.lastrowid,)).fetchone())

def list_expenses():
    db=get_db()
    return [dict(r) for r in db.execute("SELECT * FROM expenses ORDER BY id DESC")]

def list_customers():
    db=get_db()
    return [dict(r) for r in db.execute("SELECT * FROM customers ORDER BY total_spent DESC")]

def dashboard():
    db=get_db()
    active=db.execute("SELECT COUNT(*) c FROM sessions WHERE status='active'").fetchone()["c"]
    session_revenue=db.execute("SELECT COALESCE(SUM(total),0) x FROM sessions WHERE status='completed'").fetchone()["x"]
    product_revenue=db.execute("SELECT COALESCE(SUM(total),0) x FROM sales").fetchone()["x"]
    expenses=db.execute("SELECT COALESCE(SUM(amount),0) x FROM expenses").fetchone()["x"]
    low=db.execute("SELECT COUNT(*) c FROM products WHERE active=1 AND stock<=low_stock").fetchone()["c"]
    completed=db.execute("SELECT COUNT(*) c FROM sessions WHERE status='completed'").fetchone()["c"]
    sales=db.execute("SELECT COUNT(*) c FROM sales").fetchone()["c"]
    return {
        "active_sessions":active, "stations":10, "session_revenue":round(session_revenue,2),
        "product_revenue":round(product_revenue,2), "gross_revenue":round(session_revenue+product_revenue,2),
        "expenses":round(expenses,2), "net_revenue":round(session_revenue+product_revenue-expenses,2),
        "low_stock":low, "completed_sessions":completed, "product_sales":sales
    }
