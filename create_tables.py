import mysql.connector
import os

# Obtener las credenciales de acceso a la base de datos desde variables de entorno
db_host = os.environ.get('DB_HOST')
db_user = os.environ.get('DB_USER')
db_password = os.environ.get('DB_PASSWORD')
db_name = os.environ.get('DB_NAME')
db_ssl_ca = os.environ.get('DB_SSL_CA')

# Conectarse a la base de datos MySQL
conn = mysql.connector.connect(
    host=db_host,
    user=db_user,
    password=db_password,
    database=db_name
)
cursor = conn.cursor()

# Crear tabla 'urls'
cursor.execute('''
    CREATE TABLE IF NOT EXISTS urls (
        id INT AUTO_INCREMENT PRIMARY KEY,
        url VARCHAR(255) UNIQUE
    )
''')

# Crear tabla 'consultas'
cursor.execute('''
    CREATE TABLE IF NOT EXISTS consultas (
        id INT AUTO_INCREMENT PRIMARY KEY,
        fecha_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
        url_id INT
    )
''')

# Crear tabla 'historico_precios'
cursor.execute('''
    CREATE TABLE IF NOT EXISTS historico_precios (
        id INT AUTO_INCREMENT PRIMARY KEY,
        url_id INT,
        fecha_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
        consulta_id INT,
        precio_normal FLOAT,
        precio_internet FLOAT,
        precio_cmr FLOAT
    )
''')

# Cerrar la conexión
conn.close()