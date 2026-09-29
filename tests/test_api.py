import os
import tempfile
import pytest

@pytest.fixture()
def client(monkeypatch):
    from app import db
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    monkeypatch.setattr(db, "DB_PATH", __import__("pathlib").Path(path))
    from app import app
    app.config.update(TESTING=True)
    with app.app_context():
        db.init_db()
        from app.services import seed_database
        seed_database()
    with app.test_client() as c:
        yield c
    os.unlink(path)

def test_dashboard(client):
    r=client.get("/api/dashboard")
    assert r.status_code==200
    assert r.json["stations"]==10

def test_start_and_stop_session(client):
    r=client.post("/api/sessions",json={"station_id":"PS5-01","customer_name":"Test User","phone":"9999999999"})
    assert r.status_code==201
    sid=r.json["id"]
    r=client.post(f"/api/sessions/{sid}/stop",json={"payment_method":"UPI"})
    assert r.status_code==200
    assert r.json["status"]=="completed"
    assert r.json["total"]>0

def test_product_sale_reduces_stock(client):
    products=client.get("/api/products").json
    p=products[0]
    before=p["stock"]
    r=client.post("/api/sales",json={"customer_name":"Buyer","payment_method":"Cash",
                                      "items":[{"product_id":p["id"],"quantity":2}]})
    assert r.status_code==201
    after=client.get("/api/products").json
    p2=next(x for x in after if x["id"]==p["id"])
    assert p2["stock"]==before-2

def test_invalid_session(client):
    r=client.post("/api/sessions",json={"station_id":"NOPE","customer_name":"X"})
    assert r.status_code==400

def test_expense(client):
    r=client.post("/api/expenses",json={"category":"Utilities","description":"Internet","amount":500})
    assert r.status_code==201
    assert r.json["amount"]==500
