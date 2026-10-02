import os
import sqlite3
import random
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

DB_PATH = os.environ.get("SALES_DB_PATH", os.path.join(os.path.dirname(__file__), "sales.db"))

app = FastAPI(title="GestPro Sales & Analytics Service", version="1.0.0")

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
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_code TEXT UNIQUE NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            user_name TEXT NOT NULL,
            payment_method TEXT NOT NULL,
            subtotal REAL NOT NULL,
            discount REAL DEFAULT 0,
            total REAL NOT NULL,
            total_cost REAL NOT NULL
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sale_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            product_name TEXT NOT NULL,
            category_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            unit_cost REAL NOT NULL,
            unit_price REAL NOT NULL,
            subtotal REAL NOT NULL,
            FOREIGN KEY (sale_id) REFERENCES sales(id)
        );
    """)

    cursor.execute("SELECT COUNT(*) FROM sales")
    if cursor.fetchone()[0] == 0:
        seed_sales_data(conn)
    conn.close()


def seed_sales_data(conn):
    cursor = conn.cursor()
    products_catalog = [
        {"id": 1, "name": "Laptop Lenovo ThinkPad 14 Core i5", "category": "Tecnología", "cost": 2400000.0, "price": 3100000.0, "prob": 0.05},
        {"id": 2, "name": "Monitor Dell 27 Pulgadas IPS FHD", "category": "Tecnología", "cost": 650000.0, "price": 890000.0, "prob": 0.10},
        {"id": 3, "name": "Teclado Mecánico RGB Redragon Kumara", "category": "Tecnología", "cost": 120000.0, "price": 185000.0, "prob": 0.20},
        {"id": 4, "name": "Mouse Inalámbrico Logitech MX Master 3S", "category": "Tecnología", "cost": 280000.0, "price": 399000.0, "prob": 0.15},
        {"id": 6, "name": "Auriculares Sony WH-1000XM4", "category": "Audio", "cost": 850000.0, "price": 1199000.0, "prob": 0.08},
        {"id": 7, "name": "Parlante Portátil JBL Flip 6", "category": "Audio", "cost": 320000.0, "price": 480000.0, "prob": 0.12},
        {"id": 10, "name": "Hub Adaptador USB-C 7 en 1 HDMI 4K", "category": "Accesorios", "cost": 80000.0, "price": 135000.0, "prob": 0.25},
        {"id": 11, "name": "Cable HDMI 2.1 Ultra High Speed 2m", "category": "Accesorios", "cost": 25000.0, "price": 49000.0, "prob": 0.35},
        {"id": 12, "name": "Cargador Rápido GaN 65W Tipo C", "category": "Accesorios", "cost": 60000.0, "price": 110000.0, "prob": 0.22},
        {"id": 14, "name": "SSD NVMe Kingston NV2 1TB PCIe 4.0", "category": "Almacenamiento", "cost": 190000.0, "price": 280000.0, "prob": 0.18},
        {"id": 16, "name": "Memoria USB SanDisk Ultra 64GB 3.0", "category": "Almacenamiento", "cost": 18000.0, "price": 38000.0, "prob": 0.40},
        {"id": 18, "name": "Silla Ergonómica con Soporte Lumbar", "category": "Oficina & Ergonomía", "cost": 350000.0, "price": 540000.0, "prob": 0.06},
        {"id": 20, "name": "Pad Mouse Ergonómico XXL", "category": "Oficina & Ergonomía", "cost": 22000.0, "price": 48000.0, "prob": 0.28},
    ]

    payment_methods = ["Efectivo", "Tarjeta de Crédito", "Transferencia Nequi/Daviplata"]
    payment_weights = [0.45, 0.30, 0.25]
    cashiers = [
        (2, "Laura Gómez (Caja 1)"),
        (3, "Andrés Restrepo (Caja 2)")
    ]

    # Generar ventas simuladas a lo largo de los últimos 5 meses (mayo - octubre 2026)
    start_date = datetime(2026, 5, 1)
    end_date = datetime(2026, 10, 1)
    current_date = start_date
    sale_counter = 1000

    random.seed(42)  # Datos reproducibles

    while current_date <= end_date:
        # Entre 1 y 4 ventas diarias
        num_sales_day = random.randint(1, 4)
        for _ in range(num_sales_day):
            sale_counter += 1
            invoice_code = f"FAC-2026-{sale_counter:05d}"
            sale_date_str = current_date.strftime("%Y-%m-%d")
            hour = random.randint(8, 19)
            minute = random.randint(0, 59)
            time_str = f"{hour:02d}:{minute:02d}:00"

            cashier = random.choice(cashiers)
            method = random.choices(payment_methods, weights=payment_weights, k=1)[0]

            # Seleccionar entre 1 y 3 productos para la venta
            items_to_add = []
            chosen_products = random.sample(products_catalog, random.randint(1, 3))
            sale_total = 0.0
            sale_cost = 0.0

            for p in chosen_products:
                qty = random.randint(1, 2)
                subtotal = qty * p["price"]
                cost_subtotal = qty * p["cost"]
                sale_total += subtotal
                sale_cost += cost_subtotal
                items_to_add.append({
                    "product_id": p["id"],
                    "product_name": p["name"],
                    "category_name": p["category"],
                    "quantity": qty,
                    "unit_cost": p["cost"],
                    "unit_price": p["price"],
                    "subtotal": subtotal
                })

            cursor.execute("""
                INSERT INTO sales (invoice_code, date, time, user_id, user_name, payment_method, subtotal, discount, total, total_cost)
                VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?, ?)
            """, (invoice_code, sale_date_str, time_str, cashier[0], cashier[1], method, sale_total, sale_total, sale_cost))

            sale_id = cursor.lastrowid

            for item in items_to_add:
                cursor.execute("""
                    INSERT INTO sale_items (sale_id, product_id, product_name, category_name, quantity, unit_cost, unit_price, subtotal)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (sale_id, item["product_id"], item["product_name"], item["category_name"], item["quantity"], item["unit_cost"], item["unit_price"], item["subtotal"]))

        current_date += timedelta(days=1)

    conn.commit()


init_db()


@app.get("/health")
def health():
    return {
        "service": "sales_and_analytics",
        "status": "ok",
        "port": 8003
    }


@app.get("/analytics/kpis")
def get_kpis():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            COUNT(*) as total_sales,
            COALESCE(SUM(total), 0) as total_revenue,
            COALESCE(SUM(total_cost), 0) as total_cost,
            COALESCE(SUM(total - total_cost), 0) as net_profit,
            COALESCE(AVG(total), 0) as avg_ticket
        FROM sales
    """)
    row = dict(cursor.fetchone())
    conn.close()

    revenue = row["total_revenue"]
    profit = row["net_profit"]
    margin = (profit / revenue * 100) if revenue > 0 else 0.0

    row["profit_margin_pct"] = round(margin, 2)
    row["total_revenue"] = round(row["total_revenue"], 2)
    row["total_cost"] = round(row["total_cost"], 2)
    row["net_profit"] = round(row["net_profit"], 2)
    row["avg_ticket"] = round(row["avg_ticket"], 2)
    return row


@app.get("/analytics/sales-trend")
def get_sales_trend():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            SUBSTR(date, 1, 7) as month,
            COUNT(*) as transactions,
            ROUND(SUM(total), 2) as revenue,
            ROUND(SUM(total_cost), 2) as cost,
            ROUND(SUM(total - total_cost), 2) as profit
        FROM sales
        GROUP BY SUBSTR(date, 1, 7)
        ORDER BY month ASC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.get("/analytics/top-products")
def get_top_products(limit: int = 5):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            product_name,
            category_name,
            SUM(quantity) as units_sold,
            ROUND(SUM(subtotal), 2) as total_revenue,
            ROUND(SUM(subtotal - (quantity * unit_cost)), 2) as total_profit
        FROM sale_items
        GROUP BY product_id, product_name, category_name
        ORDER BY total_revenue DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.get("/analytics/by-category")
def get_sales_by_category():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            category_name,
            SUM(quantity) as units_sold,
            ROUND(SUM(subtotal), 2) as total_revenue
        FROM sale_items
        GROUP BY category_name
        ORDER BY total_revenue DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.get("/analytics/by-payment-method")
def get_sales_by_payment_method():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            payment_method,
            COUNT(*) as count,
            ROUND(SUM(total), 2) as total_amount
        FROM sales
        GROUP BY payment_method
        ORDER BY total_amount DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.get("/analytics/recent-sales")
def get_recent_sales(limit: int = 15):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, invoice_code, date, time, user_name, payment_method, total
        FROM sales
        ORDER BY date DESC, time DESC
        LIMIT ?
    """, (limit,))
    sales = [dict(r) for r in cursor.fetchall()]

    for sale in sales:
        cursor.execute("""
            SELECT product_name, quantity, unit_price, subtotal
            FROM sale_items
            WHERE sale_id = ?
        """, (sale["id"],))
        sale["items"] = [dict(item) for item in cursor.fetchall()]

    conn.close()
    return sales


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8003, reload=True)
