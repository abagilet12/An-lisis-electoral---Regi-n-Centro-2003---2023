#!/usr/bin/env python3
"""
Normaliza los .xls de "Consulta de Escrutinio por Zona" (Justicia Nacional
Electoral) a dos CSV tidy:

  resultados.csv  -> una fila por (eleccion, unidad geografica, agrupacion/lista)
  metadatos.csv   -> una fila por (eleccion, unidad geografica): padron, mesas,
                     participacion

El esquema de salida esta pensado para soportar tambien datos por seccion,
circuito o mesa: las columnas de geografia mas finas quedan vacias cuando el
archivo solo trae el agregado distrital.
"""
import csv
import re
import sys
import unicodedata
from pathlib import Path

import xlrd

RAIZ = Path(__file__).resolve().parent.parent
CRUDOS = RAIZ / "datos" / "crudos"
SALIDA = RAIZ / "datos" / "procesados"

# Codigos de distrito de la Camara Nacional Electoral
DISTRITOS = {
    "01": "Ciudad Autonoma de Buenos Aires", "02": "Buenos Aires",
    "03": "Catamarca", "04": "Cordoba", "05": "Corrientes", "06": "Chaco",
    "07": "Chubut", "08": "Entre Rios", "09": "Formosa", "10": "Jujuy",
    "11": "La Pampa", "12": "La Rioja", "13": "Mendoza", "14": "Misiones",
    "15": "Neuquen", "16": "Rio Negro", "17": "Salta", "18": "San Juan",
    "19": "San Luis", "20": "Santa Cruz", "21": "Santa Fe",
    "22": "Santiago del Estero", "23": "Tucuman", "24": "Tierra del Fuego",
}

INSTANCIAS = {
    "ELECCIONES PASO": "PASO",
    "ELECCIONES GENERALES": "GENERAL",
    "SEGUNDA VUELTA ELECTORAL": "BALOTAJE",
}

# Filas que no son agrupaciones politicas sino agregados del escrutinio
ESPECIALES = {
    "VOTOS NULOS": "nulos",
    "VOTOS RECURRIDOS": "recurridos",
    "VOTOS IMPUGNADOS": "impugnados",
    "VOTOS EN BLANCO": "blancos",
    "TOTALES": "total",
}

COLUMNAS_RESULTADOS = [
    "anio", "instancia", "fecha", "cargo",
    "distrito_id", "distrito", "seccion_id", "seccion",
    "circuito_id", "circuito", "mesa_id",
    "agrupacion_id", "agrupacion", "lista_id", "lista",
    "tipo_registro", "votos",
    "pct_general", "pct_validos", "pct_afirmativos", "pct_interna",
    "archivo_origen",
]

COLUMNAS_METADATOS = [
    "anio", "instancia", "fecha", "cargo",
    "distrito_id", "distrito", "seccion_id", "seccion",
    "circuito_id", "circuito", "mesa_id",
    "concepto", "categoria", "valor", "archivo_origen",
]


def texto(celda):
    """Normaliza el valor de una celda a str, sin el .0 de los numericos."""
    if isinstance(celda, float):
        return str(int(celda)) if celda == int(celda) else str(celda)
    return str(celda).strip()


def sin_tildes(s):
    return "".join(
        c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn"
    ).upper().strip()


def numero(celda):
    if celda == "" or celda is None:
        return ""
    if isinstance(celda, float):
        return int(celda) if celda == int(celda) else celda
    # Los valores de texto que quedan son porcentajes ("75.09%"), que en el
    # origen usan punto decimal.
    s = str(celda).strip().rstrip("%").replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return ""


def leer_encabezado(sh, archivo):
    """Extrae instancia, fecha, distrito y cargo de las primeras filas."""
    meta = {"instancia": "", "fecha": "", "distrito": "", "cargo": ""}
    for r in range(min(10, sh.nrows)):
        fila = [texto(sh.cell_value(r, c)) for c in range(sh.ncols)]
        for val in fila:
            v = sin_tildes(val)
            if v in INSTANCIAS:
                meta["instancia"] = INSTANCIAS[v]
            m = re.match(r"FECHA ELECCION:\s*(.+)", v)
            if m:
                d, mth, y = m.group(1).strip().split("/")
                meta["fecha"] = f"{y}-{mth}-{d}"
            m = re.match(r"DISTRITO:\s*(.*)", v)
            if m:
                meta["distrito"] = m.group(1).strip()
            m = re.match(r"CARGO:\s*(.*)", v)
            if m:
                meta["cargo"] = m.group(1).strip()

    # El distrito del encabezado viene truncado en algunos archivos
    # (p.ej. "Distrito: C" por Cordoba). El codigo del nombre de archivo manda.
    m = re.search(r"DIST_?(\d{2})", archivo.name, re.IGNORECASE)
    meta["distrito_id"] = m.group(1) if m else ""
    if meta["distrito_id"] in DISTRITOS:
        meta["distrito"] = DISTRITOS[meta["distrito_id"]]
    meta["anio"] = meta["fecha"][:4] if meta["fecha"] else ""
    return meta


def fila_tabla(sh):
    """Devuelve el indice de la fila de encabezado de la tabla de resultados."""
    for r in range(sh.nrows):
        if sin_tildes(texto(sh.cell_value(r, 1))) == "AGRUPACION POLITICA":
            return r
    raise ValueError("no se encontro el encabezado de la tabla")


def parsear(archivo):
    libro = xlrd.open_workbook(archivo, ignore_workbook_corruption=True)
    sh = libro.sheets()[0]
    meta = leer_encabezado(sh, archivo)
    inicio = fila_tabla(sh)

    geo = {
        "distrito_id": meta["distrito_id"], "distrito": meta["distrito"],
        "seccion_id": "", "seccion": "", "circuito_id": "", "circuito": "",
        "mesa_id": "",
    }
    comun = {
        "anio": meta["anio"], "instancia": meta["instancia"],
        "fecha": meta["fecha"], "cargo": meta["cargo"], **geo,
        "archivo_origen": archivo.name,
    }

    resultados, metadatos = [], []

    # --- Bloque de padron y mesas (entre "Inscriptos"/"Mesas" y la tabla) ---
    for r in range(inicio):
        etiqueta_izq = texto(sh.cell_value(r, 0))
        valor_izq = sh.cell_value(r, 1) if sh.ncols > 1 else ""
        etiqueta_der = texto(sh.cell_value(r, 3)) if sh.ncols > 3 else ""
        valor_der = sh.cell_value(r, 4) if sh.ncols > 4 else ""
        for etiqueta, valor, categoria in (
            (etiqueta_izq, valor_izq, "inscriptos"),
            (etiqueta_der, valor_der, "mesas"),
        ):
            if not etiqueta or sin_tildes(etiqueta) in ("INSCRIPTOS", "MESAS"):
                continue
            v = numero(valor)
            if v == "":
                continue
            et = sin_tildes(etiqueta)
            if et in ("VOTANTES", "ASISTENCIA"):
                categoria, etiqueta = "participacion", "Participacion [%]"
            metadatos.append({**comun, "concepto": etiqueta,
                              "categoria": categoria, "valor": v})

    # --- Tabla de resultados ---
    # En PASO cada agrupacion abre con una fila cabecera (sin votos), sigue con
    # sus listas internas y cierra con "TOTAL <agrupacion>". En generales y
    # balotaje hay una unica fila por agrupacion.
    agrupacion_actual = {"id": "", "nombre": ""}
    for r in range(inicio + 1, sh.nrows):
        col_id = texto(sh.cell_value(r, 0))
        nombre = texto(sh.cell_value(r, 1))
        votos = numero(sh.cell_value(r, 2))
        p_gen = numero(sh.cell_value(r, 3)) if sh.ncols > 3 else ""
        p_val = numero(sh.cell_value(r, 4)) if sh.ncols > 4 else ""
        p_afi = numero(sh.cell_value(r, 5)) if sh.ncols > 5 else ""
        if not nombre:
            continue

        clave = sin_tildes(nombre)
        if clave in ESPECIALES:
            resultados.append({**comun, "agrupacion_id": "", "agrupacion": nombre,
                               "lista_id": "", "lista": "",
                               "tipo_registro": ESPECIALES[clave], "votos": votos,
                               "pct_general": p_gen, "pct_validos": p_val,
                               "pct_afirmativos": p_afi, "pct_interna": ""})
            continue

        if clave.startswith("TOTAL "):
            resultados.append({**comun,
                               "agrupacion_id": agrupacion_actual["id"],
                               "agrupacion": agrupacion_actual["nombre"],
                               "lista_id": "", "lista": "",
                               "tipo_registro": "agrupacion", "votos": votos,
                               "pct_general": p_gen, "pct_validos": p_val,
                               "pct_afirmativos": p_afi, "pct_interna": ""})
            continue

        if votos == "":
            # Cabecera de agrupacion en PASO: abre el bloque de listas internas.
            agrupacion_actual = {"id": col_id, "nombre": nombre}
            continue

        if agrupacion_actual["nombre"] and col_id.startswith(
            agrupacion_actual["id"].split("/")[0]
        ):
            # Lista interna dentro de la agrupacion abierta (PASO).
            resultados.append({**comun,
                               "agrupacion_id": agrupacion_actual["id"],
                               "agrupacion": agrupacion_actual["nombre"],
                               "lista_id": col_id, "lista": nombre,
                               "tipo_registro": "lista", "votos": votos,
                               "pct_general": "", "pct_validos": "",
                               "pct_afirmativos": "", "pct_interna": p_gen})
        else:
            # Fila unica por agrupacion (generales / balotaje).
            agrupacion_actual = {"id": col_id, "nombre": nombre}
            resultados.append({**comun, "agrupacion_id": col_id,
                               "agrupacion": nombre, "lista_id": "", "lista": "",
                               "tipo_registro": "agrupacion", "votos": votos,
                               "pct_general": p_gen, "pct_validos": p_val,
                               "pct_afirmativos": p_afi, "pct_interna": ""})

    return resultados, metadatos


def verificar(resultados, archivo):
    """Control de consistencia: la suma de componentes debe dar el total."""
    total = next((f["votos"] for f in resultados if f["tipo_registro"] == "total"), None)
    if total is None:
        return f"{archivo}: sin fila TOTALES"
    suma = sum(
        f["votos"] for f in resultados
        if f["tipo_registro"] in ("agrupacion", "nulos", "blancos",
                                  "recurridos", "impugnados")
        and isinstance(f["votos"], (int, float))
    )
    if abs(suma - total) > 1:
        return f"{archivo}: suma {suma:,} != TOTALES {total:,} (dif {suma - total:+,})"
    return None


def main():
    archivos = sorted(CRUDOS.rglob("*.xls"))
    if not archivos:
        sys.exit(f"no hay .xls en {CRUDOS}")

    resultados, metadatos, avisos = [], [], []
    for archivo in archivos:
        res, met = parsear(archivo)
        aviso = verificar(res, archivo.name)
        if aviso:
            avisos.append(aviso)
        resultados += res
        metadatos += met
        print(f"  {archivo.name}: {len(res)} filas de resultados, "
              f"{len(met)} de metadatos")

    SALIDA.mkdir(parents=True, exist_ok=True)
    for nombre, filas, columnas in (
        ("resultados.csv", resultados, COLUMNAS_RESULTADOS),
        ("metadatos.csv", metadatos, COLUMNAS_METADATOS),
    ):
        with open(SALIDA / nombre, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=columnas)
            w.writeheader()
            w.writerows(filas)
        print(f"-> {SALIDA / nombre} ({len(filas)} filas)")

    if avisos:
        print("\nControles de consistencia:")
        for a in avisos:
            print("  !", a)
    else:
        print("\nControles de consistencia: OK en todos los archivos.")


if __name__ == "__main__":
    main()
