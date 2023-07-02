import requests
from bs4 import BeautifulSoup
import mysql.connector
from datetime import datetime
import os

# Obtener las credenciales de acceso a la base de datos desde variables de entorno
db_host = os.environ.get('DB_HOST')
db_user = os.environ.get('DB_USER')
db_password = os.environ.get('DB_PASSWORD')
db_name = os.environ.get('DB_NAME')

# Conectarse a la base de datos MySQL
conn = mysql.connector.connect(
    host=db_host,
    user=db_user,
    password=db_password,
    database=db_name
)
cursor = conn.cursor()

def insert_consulta_and_historico_precios(cursor, conn, url_id, cmr_price, internet_price, normal_price):
    """
    Insertar la consulta en la tabla 'consultas' y los precios en la tabla 'historico_precios'.
    """
    # Insertar la consulta en la tabla 'consultas'
    cursor.execute('INSERT INTO consultas (fecha_hora, url_id) VALUES (%s, %s)', (datetime.now(), url_id))
    conn.commit()

    # Obtener el ID de la consulta insertada
    consulta_id = cursor.lastrowid

    # Insertar los precios en la tabla 'historico_precios'
    cursor.execute('INSERT INTO historico_precios (consulta_id, url_id, fecha_hora, precio_cmr, precio_internet, precio_normal) VALUES (%s, %s, %s, %s, %s, %s)', (consulta_id, url_id, datetime.now(), cmr_price, internet_price, normal_price))
    conn.commit()

# Obtener todas las URLs de la tabla 'urls'
cursor.execute('SELECT id, url FROM urls')
urls = cursor.fetchall()

# Recorrer todas las URLs
for url_data in urls:
    url_id, url = url_data

    # Realizar la solicitud HTTP
    response = requests.get(url)

    # Verificar si la solicitud fue exitosa
    if response.status_code == 200:
        # Obtener el contenido HTML de la página
        html = response.text

        # Crear un objeto BeautifulSoup para analizar el HTML
        soup = BeautifulSoup(html, "html.parser")

        # Encontrar los contenedores de precios deseados
        product_containers = soup.find_all(class_="productContainer")

        if product_containers:
            # Variables para los precios
            cmr_price = None
            internet_price = None
            normal_price = None

            # Lista de posibles nombres de atributos
            data_attribute = {
                "cmr": ["data-cmr-price"],
                "internet": ["data-internet-price", "data-event-price"],
                "normal": ["data-normal-price"]
            }

            # Obtener los últimos precios registrados
            cursor.execute('SELECT precio_cmr, precio_internet, precio_normal FROM historico_precios WHERE url_id = %s ORDER BY fecha_hora DESC LIMIT 1', (url_id,))
            last_prices = cursor.fetchone()
            last_cmr_price, last_internet_price, last_normal_price = last_prices if last_prices else (None, None, None)

            # Recorrer los elementos de productContainer
            for container in product_containers:
                cmr_price = next((container.find(attrs={attr: True}).get(attr) for attr in data_attribute["cmr"] if container.find(attrs={attr: True})), None)
                internet_price = next((container.find(attrs={attr: True}).get(attr) for attr in data_attribute["internet"] if container.find(attrs={attr: True})), None)
                normal_price = next((container.find(attrs={attr: True}).get(attr) for attr in data_attribute["normal"] if container.find(attrs={attr: True})), None)
                
                if not last_prices:
                    insert_consulta_and_historico_precios(cursor, conn, url_id, cmr_price, internet_price, normal_price)
                    break

                # Comparar los precios actuales con los últimos precios registrados
                if last_cmr_price and cmr_price and float(cmr_price) < float(last_cmr_price):
                    last_cmr_price = float(last_cmr_price)
                    cmr_price = float(cmr_price)
                    if cmr_price < last_cmr_price:
                        print("Oferta encontrada (CMR)")
                        os.system(f'termux-notification --title "Oferta encontrada: ${url_id}" --content "Oferta encontrada (CMR)" --action "xdg-open ${url}"')
                if last_internet_price and internet_price:
                    last_internet_price = float(last_internet_price)
                    internet_price = float(internet_price)
                    if internet_price < last_internet_price:
                        print("Oferta encontrada (Internet)")
                        os.system(f'termux-notification --title "Oferta encontrada: ${url_id}" --content "Oferta encontrada (Internet)" --action "xdg-open ${url}"')
                if last_normal_price and normal_price:
                    last_normal_price = float(last_normal_price)
                    normal_price = float(normal_price)
                    if normal_price < last_normal_price:
                        print("Oferta encontrada (Normal)")
                        os.system(f'termux-notification --title "Oferta encontrada: ${url_id}" --content "Oferta encontrada (Normal)" --action "xdg-open ${url}"')

                if cmr_price != last_cmr_price or internet_price != last_internet_price or normal_price != last_normal_price:
                    insert_consulta_and_historico_precios(cursor, conn, url_id, cmr_price, internet_price, normal_price)
                else:
                    os.system(f'termux-notification --title "Ninguna oferta encontrada" --content "Ninguna oferta encontrada"')
        else:
            print(f"No se encontró el contenedor de precios en la URL {url}.")
    else:
        print(f"No se pudo acceder a la URL {url}. Verifica la conexión a Internet.")

# Cerrar la conexión
conn.close()