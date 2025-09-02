# sqlite_manager.py esta clase se encarga de manejar la base de datos sqlite para persistencia

import sqlite3
from pathlib import Path

# ruta del archivo sqlite (local, junto a sqlite_manager.py)
DB_PATH = Path(__file__).parent / "ticketapp.db"
# se asegura que la carpeta exista antes de crear la base de datos
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def init_db():
    """inicializa la base de datos y crea la tabla si no existe."""
    # se establece la conexion con la base de datos
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        # se crea la tabla si no existe
        c.execute("""
            CREATE TABLE IF NOT EXISTS user_sheets (
                email TEXT PRIMARY KEY,
                spreadsheet_id TEXT NOT NULL
            )
        """)
        conn.commit()
    print(f"[sqlite] init_db ejecutado. db en: {DB_PATH}")


def get_spreadsheet_id(user_email: str) -> str | None:
    """devuelve el spreadsheet_id asociado a un usuario, o none si no existe."""
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        # se busca el spreadsheet_id por email
        c.execute("SELECT spreadsheet_id FROM user_sheets WHERE email=?", (user_email,))
        row = c.fetchone()
    # se devuelve el resultado o none si no se encuentra
    return row[0] if row else None


def set_spreadsheet_id(user_email: str, spreadsheet_id: str):
    """guarda o actualiza el spreadsheet_id asociado a un usuario."""
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        # se inserta el id o se actualiza si ya existe
        c.execute("""
            INSERT INTO user_sheets (email, spreadsheet_id)
            VALUES (?, ?)
            ON CONFLICT(email) DO UPDATE SET spreadsheet_id=excluded.spreadsheet_id
        """, (user_email, spreadsheet_id))
        conn.commit()
    print(f"[sqlite] spreadsheet_id guardado para {user_email}")