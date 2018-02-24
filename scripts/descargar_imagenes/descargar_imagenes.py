from bs4 import BeautifulSoup
import urllib.request
import urllib.parse
import os
import argparse
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import json
import time
import lxml

def descargar_imagenes():
    parser = argparse.ArgumentParser()
    parser.add_argument('-q', '--query', help='Búsqueda a realizar', type=str, required=True)
    parser.add_argument('-f', '--folder', help='Nombre de la carpeta', type=str, required=False, default="Resultados")
    parser.add_argument('-c', '--count', help='Cantidad de imágenes a descargar', type=int, required=False, default=100)
    parser.add_argument('-n', '--number', help='Número por el cual empezar a numerar las imágenes', type=int, required=False, default=0)
    parser.add_argument('-r', '--root', help='Nombre raíz de los archivos descargados', type=str, required=False, default="")
    args = parser.parse_args()
    nombreRaizImagen = args.root
    if nombreRaizImagen == "":
        nombreRaizImagen = args.query
    busqueda = args.query.replace(" ", "+")
    nombreCarpeta = args.folder
    total = args.count

    # Path al geckodriver de Firefox
    os.environ["PATH"] += os.pathsep + os.getcwd()

    # Cantidad de scrolls * 400 imágenes que se abrirán en el navegador
    # Sumo 1 al total porque la primer imagen devuelta no pertenece a la búsqueda
    scrolls = int((total + 1) / 400 + 1)

    urlBusqueda = "https://www.google.com.ar/search?q=" + busqueda + "&dcr=0&source=lnms&tbs=sur:fmc&tbm=isch&sa=X&ved=0ahUKEwjhpI_H5aHZAhXHTZAKHWnRBGgQ_AUICigB&biw=1366&bih=631&as_rights=(cc_publicdomain|cc_attribute|cc_sharealike).-(cc_noncommercial|cc_nonderived)"

    driver = webdriver.Firefox()
    driver.get(urlBusqueda)

    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
           'Accept-Encoding': 'none',
           'Accept-Language': 'en-US,en;q=0.8',
           'Connection': 'keep-alive'}
    request = urllib.request.Request(urlBusqueda, headers = headers)
    fetcher = urllib.request.build_opener()

    # Se busca el directorio indicado y se crea en caso de no existir
    directorios = os.listdir()
    carpetaExistente = False
    for directorio in directorios:
        if directorio == nombreCarpeta:
            carpetaExistente = True
    if not carpetaExistente:
        os.mkdir(nombreCarpeta)

    # Se realizan los scrolls necesarios
    for _ in range(scrolls):
        for __ in range(10):
            # Scrolls necesarios para mostrar 400 imágenes
            driver.execute_script("window.scrollBy(0, 1000000)")
            time.sleep(0.2)
        time.sleep(0.5)
        try:
            driver.find_element_by_xpath("//input[@value='Más resultados']").click()
        except Exception as e:
            print("No se hallaron tantas imágenes:", e)
            break

    print("Esperando 5 segundos")
    time.sleep(5)
    print("Continúa ejecución")

    soup = BeautifulSoup(driver.page_source, 'lxml')

    imagenes = []
    # Sumo 1 al total porque la primer imagen devuelta no pertenece a la búsqueda
    imagenes = soup.findAll('img', limit = int(total + 1))

    contador = 0
    totalDescargadas = 0

    for imagen in imagenes:
        if contador == 0:
            contador += 1
        else:
            try:
                print("Descargando", contador, "de", total)
                enlace = imagen.attrs.get('src')
                if enlace != None:
                    urllib.request.urlretrieve(enlace, nombreCarpeta + "\\" + nombreRaizImagen +  str(args.number + contador - 1) +  ".jpg")
                    totalDescargadas += 1
            except Exception as e:
                print("La descarga falló:", e)
            finally:
                print
            if contador >= total:
                break
            else:
                contador += 1

    print("Pudieron descargarse", totalDescargadas, "de las", total, "pedidas")

    driver.quit()

# Ejemplo de uso
# py descargar_imagenes -q "Ovejero aleman" -f "Ovejeros alemanes" -c 50
descargar_imagenes()
