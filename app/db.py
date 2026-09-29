import sqlite3
from pathlib import Path
from flask import g

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "gamingstation.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS stations (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    group_name TEXT NOT NULL,
    rate REAL NOT NULL,
    status TEXT NOT NULL DEFAULT 'available'
);

CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT UNIQUE,
    visits INTEGER NOT NULL DEFAULT 0,
    total_spent REAL NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    station_id TEXT NOT NULL,
    customer_name TEXT NOT NULL,
    phone TEXT,
    started_at TEXT NOT NULL,
    ended_at TEXT,
    duration_minutes INTEGER,
    rate REAL NOT NULL,
    total REAL NOT NULL DEFAULT 0,
    payment_method TEXT,
    status TEXT NOT NULL DEFAULT 'active',
    FOREIGN KEY(station_id) REFERENCES stations(id)
);

CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sku TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    price REAL NOT NULL,
    stock INTEGER NOT NULL DEFAULT 0,
    low_stock INTEGER NOT NULL DEFAULT 5,
    active INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name TEXT,
    phone TEXT,
    subtotal REAL NOT NULL,
    discount REAL NOT NULL DEFAULT 0,
    tax REAL NOT NULL DEFAULT 0,
    total REAL NOT NULL,
    payment_method TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sale_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sale_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price REAL NOT NULL,
    total REAL NOT NULL,
    FOREIGN KEY(sale_id) REFERENCES sales(id),
    FOREIGN KEY(product_id) REFERENCES products(id)
);

CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,
    description TEXT NOT NULL,
    amount REAL NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""

def get_db():
    if "db" not in g:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db

def init_db():
    db = get_db()
    db.executescript(SCHEMA)
    db.commit()

def close_db(_error=None):
    db = g.pop("db", None)
    if db:
        db.close()
