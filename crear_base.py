import sqlite3

conn = sqlite3.connect("supermercado.db")
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS inventario")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS inventario (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        region TEXT,
        comuna TEXT,
        sucursal TEXT,
        producto TEXT,
        lote TEXT,
        dias_vencer INTEGER,
        temperatura REAL,
        frescura_ia REAL,
        descuento_aplicado INTEGER,
        precio_original INTEGER,
        precio_final INTEGER
    )
""")

conn.commit()
conn.close()
print("✅ Base de datos lista con soporte para Comunas (Buin/Puente Alto).")