# database.py
import sqlite3
import json
from datetime import datetime

DB_FILE = "log_publico.db"

def init_db():
    """
    Inicializa la base de datos y crea la tabla si no existe.
    Es seguro llamar a esta función cada vez que se inicia la app.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # Creamos la tabla 'interacciones' si no existe ya
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

def guardar_interaccion(pregunta, clasificacion, dato_recuperado, respuesta_final):
    """
    Guarda una nueva interacción en la base de datos.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Preparamos los datos para la inserción
    interaction_data = (
        datetime.now().isoformat(),
        pregunta,
        json.dumps(clasificacion, ensure_ascii=False), # Guardamos el diccionario como un string JSON
        str(dato_recuperado), # Aseguramos que el dato sea un string
        respuesta_final
    )
    
    # Usamos '?' para evitar inyección de SQL, es la forma segura de insertar datos
    cursor.execute("""
    INSERT INTO interacciones (timestamp, pregunta, clasificacion_json, dato_recuperado, respuesta_final)
    VALUES (?, ?, ?, ?, ?)
    """, interaction_data)
    
    conn.commit()
    conn.close()