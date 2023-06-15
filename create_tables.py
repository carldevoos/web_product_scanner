import sqlite3

# Conectarse a la base de datos o crear una nueva si no existe
conn = sqlite3.connect('scanner.db')
cursor = conn.cursor()

# Crear tabla 'urls'
cursor.execute('''
    CREATE TABLE IF NOT EXISTS urls (
        id INTEGER PRIMARY KEY ,
        url TEXT UNIQUE
    )
''')

# Crear tabla 'consultas'
cursor.execute('''
    CREATE TABLE IF NOT EXISTS consultas (
        id INTEGER PRIMARY KEY,
        fecha_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
        url_id INTEGER,
        FOREIGN KEY (url_id) REFERENCES urls (id)
    )
''')

# Crear tabla 'historico_precios'
cursor.execute('''
    CREATE TABLE IF NOT EXISTS historico_precios (
        id INTEGER PRIMARY KEY,
        url_id INTEGER,
        fecha_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
        consulta_id INTEGER,
        precio_normal FLOAT,
        precio_internet FLOAT,
        precio_cmr FLOAT,
        FOREIGN KEY (consulta_id) REFERENCES consultas (id)
    )
''')

# Guardar los cambios y cerrar la conexión
conn.commit()
conn.close()