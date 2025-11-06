#!/usr/bin/env python3.13

# Sincroniza todos los HTML de la carpeta, actualizando el footer y menú para que sean iguales
# en todas las páginas. Hace copia de seguridad (.old) de los archivos modificados, que no
# suben al repositorio (se quean solo en local).
#
# Las plantillas a sustituir estarán en la carpeta 'plantillas'. En el HTML, se debe marcar el
# inicio y fin de la zona a sustituir con dos líneas cuyo ÚNICO contenido (in indentación ni
# caracteres blancos antes del newline) sea:
# <!-- BEGIN nombre_plantilla -->
# <!-- END nombre_plantilla -->
# donde 'nombre_plantilla' es el nombre del archivo plantilla (p.e. <!-- BEGIN _footer.html -->).
# Cuando haya referencias a archivos se usará el patrón {{carpeta}} como prefijo del nombre de
# archivo, como  p.e. "{{carpeta}}images/img01.png", que se sustituirá, dependiendo de la
# localización del HTML, como "images/img01,png" o "../images/img01,png", etc. La variable global
# 'elementos' indica la carpeta donde sustituir HTMLs, y el prefijo de las referencias para los
# HTML de cada carpeta en cuestión.

import os
import sys


def sincroniza(archivo: str, prefix: str) -> None:
    """Actualiza el archivo indicado (típicamente un HTML) con las plantillas pertinentes. Deja la
    versión antigua en un archivo OLD.

    :param archivo: path completo del archivo a actualizar
    :param prefix: string con el que sustituir {{carpeta}} en el HTML
    :return: nada
    """
    changed = False
    print(f"Actualizando '{os.path.basename(archivo)}' (prefijo '{prefix}')...")
    plantillas_path = os.path.dirname(archivo)
    # Leemos las líneas del archivo a actualizar:
    with open(archivo, "rt") as f:
        lineas_in = f.readlines()
    path_base = os.path.dirname(os.path.abspath(sys.argv[0]))    # carpeta de la aplicación
    path_plantillas = os.path.join(path_base, "plantillas")    # carpeta de las plantillas
    plantillas = os.listdir(path_plantillas)    # nombres de los archivos plantilla
    # Vamos a procesar cada plantilla en el directorio 'plantillas':
    for plantilla in plantillas:
        plantilla_full = os.path.join(path_plantillas, plantilla)
        print(f"    Procesando plantilla '{plantilla}'...")
        # Leemos las líneas de la plantilla:
        with open(plantilla_full, "rt") as f:
            lineas_plantilla = f.readlines()
        # Comprobamos si la plantilla es sustituible en el archivo:
        sustituible = True
        try:
            index_begin = lineas_in.index(f"<!-- BEGIN {plantilla} -->\n")
            index_end = lineas_in.index(f"<!-- END {plantilla} -->\n")
            if index_begin > index_end:
                sustituible = False
        except ValueError:
            sustituible = False
        if not sustituible:
            print(f"\033[31m        ¡Plantilla '{plantilla}' no sustituible!\033[0m")
            continue    # si no es sustituible en el archivo, pasamos a la siguiente plantilla
        # Vamos a procesar esta plantilla:
        changed = True
        # Vamos a sustituir la plantilla:
        lineas_out = []
        # Vamos añadiendo al resultado las que no pertenecen a la zona a sustituir:
        skip = False    # nos saltaríamos las líneas a sustitur
        for linea in lineas_in:
            if skip:    # será True cuando nos estemos saltando las líneas ANTIGUAS a sustituir
                if linea == f"<!-- END {plantilla} -->\n":
                    lineas_out.append(linea)    # añadimos marcador y dejamos de saltar
                    skip = False
                continue
            # Añadimos la línea al resultado:
            lineas_out.append(linea)
            # Si hemos añadido el marcador de inicio, vamos a añadir también las líneas NUEVAS de la plantilla:
            if linea == f"<!-- BEGIN {plantilla} -->\n":
                for linea_nueva in lineas_plantilla:
                    lineas_out.append(linea_nueva.replace("{{carpeta}}", prefix))
                # Después de esto, nos saltaremos las líneas antiguas de entrada hasta el marcador final (no incluido):
                skip = True
        # Antes de pasar a la siguiente plantilla, actualizamos 'lineas_in':
        lineas_in = lineas_out
    # En este punto ya tenemos en líneas_in el contenido sustituido. Si se ha cambiado algo, procedamos a actualizar:
    if changed:
        # Vamos a renombrar el antiguo archivo añadiendo '.old':
        os.rename(archivo, archivo + ".old")
        # Vamos a crear el nuevo:
        with open(archivo, "wt") as f:
            for linea in lineas_in:
                f.write(linea)


for elemento in [
    ("", ""),
    ("cursos", "../")
]:    # carpetas a sincronizar (HTMLs) + prefijo referencias
    carpeta, prefijo = elemento
    carpeta_full = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), carpeta)
    archivos = os.listdir(carpeta_full)
    # Vamos a sincronizar todos los archivos HTML de la carpeta:
    for archivo in archivos:
        archivo_full = os.path.join(carpeta_full, archivo)
        if os.path.isfile(archivo_full) and \
                archivo.endswith(".html"):
            sincroniza(archivo_full, prefijo)
