import os
import sqlite3
from typing import Optional, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

DB_PATH = os.environ.get("USERS_DB_PATH", os.path.join(os.path.dirname(__file__), "users.db"))

app = FastAPI(title="GestPro Users & Auth Service", version="1.0.0")

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
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin', 'vendedor')),
            active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Sembrar usuarios por defecto si la tabla está vacía
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        default_users = [
            ("admin", "Carlos Mendoza (Gerente Comercial)", "gerencia@gestpro.com", "admin", 1),
            ("cajero1", "Laura Gómez (Cajera Principal)", "laura.gomez@gestpro.com", "vendedor", 1),
            ("cajero2", "Andrés Restrepo (Vendedor Mostrador)", "andres.restrepo@gestpro.com", "vendedor", 1),
        ]
        cursor.executemany(
            "INSERT INTO users (username, full_name, email, role, active) VALUES (?, ?, ?, ?, ?)",
            default_users
        )
        conn.commit()
    conn.close()


init_db()


class LoginRequest(BaseModel):
    username: str


class UserResponse(BaseModel):
    id: int
    username: str
    full_name: str
    email: str
    role: str
    active: int


@app.get("/health")
def health():
    return {
        "service": "users_and_auth",
        "status": "ok",
        "port": 8001
    }


@app.get("/users/", response_model=List[UserResponse])
def get_users():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, full_name, email, role, active FROM users WHERE active = 1")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


@app.get("/users/{user_id}", response_model=UserResponse)
def get_user_by_id(user_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, full_name, email, role, active FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return dict(row)


@app.post("/users/login")
def login(req: LoginRequest):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, full_name, email, role, active FROM users WHERE username = ?", (req.username.strip(),))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas o usuario no registrado")
    user = dict(row)
    if user["active"] != 1:
        raise HTTPException(status_code=403, detail="Usuario inactivo")
    return {
        "status": "success",
        "user": user,
        "token": f"gestpro_token_{user['role']}_{user['id']}"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
