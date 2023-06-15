import requests
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime
import os

# Conectarse a la base de datos
conn = sqlite3.connect('scanner.db')
cursor = conn.cursor()

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
            cursor.execute('SELECT precio_cmr, precio_internet, precio_normal FROM historico_precios WHERE url_id = ? ORDER BY fecha_hora DESC LIMIT 1', (url_id,))
            last_prices = cursor.fetchone()
            last_cmr_price, last_internet_price, last_normal_price = last_prices if last_prices else (None, None, None)

            # Recorrer los elementos de productContainer
            for container in product_containers:
                cmr_price = next((container.find(attrs={attr: True}).get(attr) for attr in data_attribute["cmr"] if container.find(attrs={attr: True})), None)
                internet_price = next((container.find(attrs={attr: True}).get(attr) for attr in data_attribute["internet"] if container.find(attrs={attr: True})), None)
                normal_price = next((container.find(attrs={attr: True}).get(attr) for attr in data_attribute["normal"] if container.find(attrs={attr: True})), None)
                
                # Comparar los precios actuales con los últimos precios registrados
                if last_cmr_price and cmr_price and float(cmr_price) < float(last_cmr_price):
                    print("Oferta encontrada (CMR)")
                    os.system(f'termux-notification --title "Oferta encontrada: ${url_id}" --content "Oferta encontrada (CMR)"')
                if last_internet_price and internet_price and float(internet_price) < float(last_internet_price):
                    print("Oferta encontrada (Internet)")
                    os.system(f'termux-notification --title "Oferta encontrada: ${url_id}" --content "Oferta encontrada (Internet)"')
                if last_normal_price and normal_price and float(normal_price) < float(last_normal_price):
                    print("Oferta encontrada (Normal)")
                    os.system(f'termux-notification --title "Oferta encontrada: ${url_id}" --content "Oferta encontrada (Normal)"')

                # Insertar la consulta en la tabla 'consultas'
                cursor.execute('INSERT INTO consultas (fecha_hora, url_id) VALUES (?, ?)', (datetime.now(), url_id))
                conn.commit()

                # Obtener el ID de la consulta insertada
                consulta_id = cursor.lastrowid

                # Insertar los precios en la tabla 'historico_precios'
                cursor.execute('INSERT INTO historico_precios (consulta_id, url_id, fecha_hora, precio_cmr, precio_internet, precio_normal) VALUES (?, ?, ?, ?, ?, ?)', (consulta_id, url_id, datetime.now(), cmr_price, internet_price, normal_price))
                conn.commit()
        
            print(f"Los precios de la URL {url} se han guardado en la base de datos.")
        else:
            print(f"No se encontró el contenedor de precios en la URL {url}.")
    else:
        print(f"No se pudo acceder a la URL {url}. Verifica la conexión a Internet.")

# Cerrar la conexión
conn.close()