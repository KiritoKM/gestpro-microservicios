import os
import sqlite3
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

DB_PATH = os.environ.get("INVENTORY_DB_PATH", os.path.join(os.path.dirname(__file__), "inventory.db"))

app = FastAPI(title="GestPro Inventory & Catalog Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sku TEXT UNIQUE NOT NULL,
            barcode TEXT,
            name TEXT NOT NULL,
            category_id INTEGER NOT NULL,
            category_name TEXT NOT NULL,
            cost REAL NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL DEFAULT 0,
            min_stock INTEGER NOT NULL DEFAULT 5,
            unit TEXT DEFAULT 'UND',
            active INTEGER DEFAULT 1,
            FOREIGN KEY (category_id) REFERENCES categories(id)
        );
    """)

    # Sembrar catálogo inicial representativo de GestPro si está vacío
    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        categories = [
            (1, "Tecnología"),
            (2, "Audio"),
            (3, "Accesorios"),
            (4, "Almacenamiento"),
            (5, "Oficina & Ergonomía")
        ]
        cursor.executemany("INSERT OR IGNORE INTO categories (id, name) VALUES (?, ?)", categories)

        products = [
            ("SKU-TEC-001", "7701001", "Laptop Lenovo ThinkPad 14 Core i5", 1, "Tecnología", 2400000.0, 3100000.0, 12, 4),
            ("SKU-TEC-002", "7701002", "Monitor Dell 27 Pulgadas IPS FHD", 1, "Tecnología", 650000.0, 890000.0, 8, 3),
            ("SKU-TEC-003", "7701003", "Teclado Mecánico RGB Redragon Kumara", 1, "Tecnología", 120000.0, 185000.0, 25, 5),
            ("SKU-TEC-004", "7701004", "Mouse Inalámbrico Logitech MX Master 3S", 1, "Tecnología", 280000.0, 399000.0, 15, 4),
            ("SKU-TEC-005", "7701005", "Tablet Samsung Galaxy Tab A9", 1, "Tecnología", 480000.0, 680000.0, 3, 5),  # Alerta bajo stock

            ("SKU-AUD-001", "7702001", "Auriculares Sony WH-1000XM4 Noise Cancelling", 2, "Audio", 850000.0, 1199000.0, 6, 2),
            ("SKU-AUD-002", "7702002", "Parlante Portátil JBL Flip 6 Waterproof", 2, "Audio", 320000.0, 480000.0, 18, 5),
            ("SKU-AUD-003", "7702003", "Micrófono USB HyperX SoloCast", 2, "Audio", 160000.0, 245000.0, 9, 3),
            ("SKU-AUD-004", "7702004", "Audífonos In-Ear Xiaomi Redmi Buds 5", 2, "Audio", 75000.0, 130000.0, 2, 8),  # Alerta bajo stock

            ("SKU-ACC-001", "7703001", "Hub Adaptador USB-C 7 en 1 HDMI 4K", 3, "Accesorios", 80000.0, 135000.0, 30, 8),
            ("SKU-ACC-002", "7703002", "Cable HDMI 2.1 Ultra High Speed 2m", 3, "Accesorios", 25000.0, 49000.0, 45, 10),
            ("SKU-ACC-003", "7703003", "Cargador Rápido GaN 65W Tipo C", 3, "Accesorios", 60000.0, 110000.0, 22, 6),
            ("SKU-ACC-004", "7703004", "Soporte Ajustable de Aluminio para Laptop", 3, "Accesorios", 45000.0, 85000.0, 14, 5),

            ("SKU-ALM-001", "7704001", "SSD NVMe Kingston NV2 1TB PCIe 4.0", 4, "Almacenamiento", 190000.0, 280000.0, 20, 5),
            ("SKU-ALM-002", "7704002", "Disco Externo Seagate 2TB USB 3.0", 4, "Almacenamiento", 210000.0, 315000.0, 11, 4),
            ("SKU-ALM-003", "7704003", "Memoria USB SanDisk Ultra 64GB 3.0", 4, "Almacenamiento", 18000.0, 38000.0, 50, 12),
            ("SKU-ALM-004", "7704004", "SSD SATA Crucial BX500 480GB", 4, "Almacenamiento", 110000.0, 175000.0, 0, 5),  # Agotado

            ("SKU-OFI-001", "7705001", "Silla Ergonómica con Soporte Lumbar", 5, "Oficina & Ergonomía", 350000.0, 540000.0, 7, 2),
            ("SKU-OFI-002", "7705002", "Lámpara LED de Escritorio con Carga Qi", 5, "Oficina & Ergonomía", 70000.0, 125000.0, 16, 4),
            ("SKU-OFI-003", "7705003", "Pad Mouse Ergonómico XXL Impermeable", 5, "Oficina & Ergonomía", 22000.0, 48000.0, 40, 10),
        ]

        cursor.executemany("""
            INSERT INTO products (sku, barcode, name, category_id, category_name, cost, price, stock, min_stock)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, products)
        conn.commit()
    conn.close()


init_db()


class ProductResponse(BaseModel):
    id: int
    sku: str
    barcode: Optional[str]
    name: str
    category_id: int
    category_name: str
    cost: float
    price: float
    stock: int
    min_stock: int
    unit: str
    active: int


@app.get("/health")
def health():
    return {
        "service": "inventory_and_catalog",
        "status": "ok",
        "port": 8002
    }


@app.get("/inventory/categories")
def get_categories():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM categories ORDER BY name")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.get("/inventory/products")
def get_products(
    search: Optional[str] = Query(None, description="Búsqueda por nombre o SKU"),
    category_id: Optional[int] = Query(None, description="Filtrar por ID de categoría"),
    low_stock_only: bool = Query(False, description="Filtrar solo productos en stock crítico")
):
    conn = get_db()
    cursor = conn.cursor()
    query = "SELECT * FROM products WHERE active = 1"
    params = []

    if search:
        query += " AND (name LIKE ? OR sku LIKE ? OR barcode LIKE ?)"
        term = f"%{search.strip()}%"
        params.extend([term, term, term])

    if category_id:
        query += " AND category_id = ?"
        params.append(category_id)

    if low_stock_only:
        query += " AND stock <= min_stock"

    query += " ORDER BY name ASC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.get("/inventory/products/{product_id}")
def get_product_by_id(product_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return dict(row)


@app.get("/inventory/low-stock")
def get_low_stock():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE active = 1 AND stock <= min_stock ORDER BY stock ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.get("/inventory/stats")
def get_inventory_stats():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            COUNT(*) as total_products,
            SUM(stock) as total_units,
            SUM(stock * cost) as total_inventory_cost,
            SUM(stock * price) as total_inventory_retail_value,
            SUM(CASE WHEN stock <= min_stock THEN 1 ELSE 0 END) as low_stock_count,
            SUM(CASE WHEN stock = 0 THEN 1 ELSE 0 END) as out_of_stock_count
        FROM products WHERE active = 1
    """)
    row = cursor.fetchone()
    conn.close()
    return dict(row)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True)
