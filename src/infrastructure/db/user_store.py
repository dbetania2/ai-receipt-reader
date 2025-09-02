# user_sotre.py esta clase maneja el almacenamiento de datos del usuario en sqlite

import sqlite3
import os

# se define la ruta de la base de datos
DB_PATH = os.path.join(os.path.dirname(__file__), "users.db")

def init_db():
    # se inicializa la base de datos y se crea la tabla de usuarios
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # se crea la tabla si no existe
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            spreadsheet_id TEXT
        )
    ''')
    conn.commit()
    conn.close()

def get_sheet_id_for(email: str):
    # se obtiene el id de la hoja de calculo del usuario
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # se busca el id por el email
    c.execute('SELECT spreadsheet_id FROM users WHERE email=?', (email,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

def set_sheet_id_for(email: str, sheet_id: str):
    # se guarda o actualiza el id de la hoja de calculo del usuario
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # se inserta o reemplaza el registro
    c.execute('INSERT OR REPLACE INTO users (email, spreadsheet_id) VALUES (?, ?)', (email, sheet_id))
    conn.commit()
    conn.close()
