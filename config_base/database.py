# database.py
import sqlite3
import json
import os
from datetime import datetime

# Intentamos importar el driver de Postgres. 
# Si no está instalado en tu máquina local, no rompe el código, solo usará SQLite.
try:
    import psycopg2
except ImportError:
    psycopg2 = None

DB_FILE = "log_publico.db"

def _obtener_url_postgres():
    """Busca la URL de la base de datos en las variables de entorno (Streamlit Cloud)."""
    return os.getenv("DATABASE_URL")

def init_db():
    """
    Inicializa la base de datos (Postgres en la nube o SQLite local).
    """
    url = _obtener_url_postgres()

    if url and psycopg2:
        # --- MODO NUBE (POSTGRESQL / NEON) ---
        try:
            conn = psycopg2.connect(url)
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS interacciones (
                id SERIAL PRIMARY KEY,
                timestamp TEXT NOT NULL,
                pregunta TEXT NOT NULL,
                clasificacion_json TEXT,
                dato_recuperado TEXT,
                respuesta_final TEXT
            )
            """)
            conn.commit()
            cursor.close()
            conn.close()
            print("Base de datos POSTGRESQL inicializada.")
        except Exception as e:
            print(f"Error inicializando Postgres: {e}")
    else:
        # --- MODO LOCAL (SQLITE) ---
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS interacciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            pregunta TEXT NOT NULL,
            clasificacion_json TEXT,
            dato_recuperado TEXT,
            respuesta_final TEXT
        )
        """)
        conn.commit()
        conn.close()
        print("Base de datos SQLITE inicializada.")

def guardar_interaccion(pregunta, clasificacion, dato_recuperado, respuesta_final):
    """
    Guarda una nueva interacción en la base de datos.
    """
    timestamp = datetime.now().isoformat()
    clasificacion_str = json.dumps(clasificacion, ensure_ascii=False)
    dato_str = str(dato_recuperado)

    url = _obtener_url_postgres()

    if url and psycopg2:
        # --- MODO NUBE (POSTGRESQL / NEON) ---
        try:
            conn = psycopg2.connect(url)
            cursor = conn.cursor()

            # Nota: psycopg2 usa %s en lugar de ? para la inserción segura
            interaction_data = (timestamp, pregunta, clasificacion_str, dato_str, respuesta_final)
            cursor.execute("""
            INSERT INTO interacciones (timestamp, pregunta, clasificacion_json, dato_recuperado, respuesta_final)
            VALUES (%s, %s, %s, %s, %s)
            """, interaction_data)

            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Error guardando en Postgres: {e}")
    else:
        # --- MODO LOCAL (SQLITE) ---
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        interaction_data = (timestamp, pregunta, clasificacion_str, dato_str, respuesta_final)

        # SQLite usa ? para la inserción segura
        cursor.execute("""
        INSERT INTO interacciones (timestamp, pregunta, clasificacion_json, dato_recuperado, respuesta_final)
        VALUES (?, ?, ?, ?, ?)
        """, interaction_data)

        conn.commit()
        conn.close()