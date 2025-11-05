#!/usr/bin/env python3.13

# Sincroniza todos los HTML de la carpeta, actualizando el footer y menú para que sean iguales en todas las páginas.
#
# En cada carpeta debe haber su correspondiente _footer.html y _menu.html; en lás páginas se debe marcar el inicio
# y fin de la zona a sustituir con dos líneas cuyo ÚNICO contenido sea <!-- BEGIN _footer.html --> y <!-- END _footer.html -->
# para el footer o <!-- BEGIN _footer.html --> y <!-- END _footer.html --> para el menú. Esas líneas deben ir sin
# indentación ni caracteres blancos antes del newline.

import os
import sys


def sincroniza(archivo: str) -> None:
    """Actualiza los elementos footer y menu del archivo. Deja el anterior en un archivo OLD.

    :param archivo: path completo del archivo a actualizar
    :return: nada
    """
    global plantillas
    changed = False
    print(f"Actualizando '{os.path.basename(archivo)}'...")
    carpeta = os.path.dirname(archivo)    # carpeta del archivo a procesar
    # Leemos las líneas del archivo a actualizar:
    with open(archivo, "rt") as f:
        lineas_in = f.readlines()
    # Buscamos y leemos las plantillas en la carpeta:
    for plantilla in plantillas:
        plantilla_full = os.path.join(carpeta, plantilla)
        if os.path.exists(plantilla_full) and os.path.isfile(plantilla_full):
            print(f"    Procesando plantilla '{plantilla}'...")
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
            if sustituible:
                changed = True
                # Vamos a sustituir la plantilla:
                lineas_out = []
                # Vamos añadiendo al resultado las que no pertenecen a la zona a sustituir:
                skip = False
                for linea in lineas_in:
                    if skip:    # será True cuando nos estemos saltando las líneas ANTIGUAS a sustituir
                        if linea == f"<!-- END {plantilla} -->\n":
                            lineas_out.append(linea)    # añadimos marcador y dejamos de saltar
                            skip = False
                        continue
                    lineas_out.append(linea)
                    # Si hemos añadido el marcador de inicio, vamos a añadir las líneas NUEVAS de la plantilla:
                    if linea == f"<!-- BEGIN {plantilla} -->\n":
                        lineas_out.extend(lineas_plantilla)
                        skip = True    # y vamos a saltarnos las ANTIGUAS hasta el marcador final (no incluido)
                # Vamos a cambiar las líneas de entrada a la nueva versión:
                lineas_in = lineas_out
            else:
                print(f"\033[31m¡Plantilla '{plantilla}' no sustituible!\033[0m")
        else:
            print(f"\033[31m¡Plantilla '{plantilla}' no encontrada!\033[0m")
    # En este punto ya tenemos en líneas_in el contenido sustituido. Si se ha cambiado algo, procedamos a actualizar:
    if changed:
        # Vamos a renombrar el antiguo archivo añadiendo '.old':
        os.rename(archivo, archivo + ".old")
        # Vamos a crear el nuevo:
        with open(archivo, "wt") as f:
            for linea in lineas_in:
                f.write(linea)


carpetas = ["", "cursos"]    # carpetas donde aplicar la sincronización
plantillas = ["_footer.html", "_menu.html"]    # archivos plantilla

path_base = os.path.dirname(os.path.abspath(sys.argv[0]))
for carpeta in carpetas:
    carpeta_full = os.path.join(path_base, carpeta)
    archivos = os.listdir(carpeta_full)
    for archivo in archivos:
        archivo_full = os.path.join(carpeta_full, archivo)
        if os.path.isfile(archivo_full) and \
                archivo.endswith(".html") and \
                archivo not in plantillas:
            sincroniza(archivo_full)

