#!/usr/bin/env python3
"""
Normaliza los .xlsx "Votos por Localidad" (Santa Fe, categoria Presidente) al
mismo esquema tidy que scripts/parse_escrutinio_zona.py, agregando las
columnas de localidad y circuito.

Cada .xlsx trae seis hojas; se usan cuatro:
  Votos por Localidad          -> votos por agrupacion
  Totales por Tipo de Voto     -> blancos, nulos, impugnados, recurridos,
                                  comando y el total de positivos
  Electores y Mesas            -> padron y mesas por localidad
  Nomenclador Circuito-Localidad -> el puente circuito -> localidad
La hoja "Agrupacion Ganadora por Local" es derivada y se ignora: se puede
recalcular desde los votos.

Salida:
  datos/procesados/resultados_localidad.csv
  datos/procesados/metadatos_localidad.csv
  datos/procesados/nomenclador_circuito_localidad.csv
"""
import csv
import re
import sys
from pathlib import Path

import openpyxl

RAIZ = Path(__file__).resolve().parent.parent
CRUDOS = RAIZ / "datos" / "crudos" / "localidad"
SALIDA = RAIZ / "datos" / "procesados"

DISTRITO_ID, DISTRITO, CARGO = "21", "Santa Fe", "PRESIDENTE Y VICE"

FECHAS = {
    ("2003", "GENERAL"): "2003-04-27",
    ("2007", "GENERAL"): "2007-10-28",
    ("2011", "PASO"): "2011-08-14", ("2011", "GENERAL"): "2011-10-23",
    ("2015", "PASO"): "2015-08-09", ("2015", "GENERAL"): "2015-10-25",
    ("2015", "BALOTAJE"): "2015-11-22",
    ("2019", "PASO"): "2019-08-11", ("2019", "GENERAL"): "2019-10-27",
    ("2023", "PASO"): "2023-08-13", ("2023", "GENERAL"): "2023-10-22",
    ("2023", "BALOTAJE"): "2023-11-19",
}

# Columnas de la hoja "Totales por Tipo de Voto" -> tipo_registro de salida.
# POSITIVO no es un tipo de voto mas: es la suma de las agrupaciones, y se
# usa para validar.
TIPOS_VOTO = {
    "EN BLANCO": "blancos", "NULO": "nulos", "IMPUGNADO": "impugnados",
    "RECURRIDO": "recurridos", "COMANDO": "comando", "POSITIVO": "positivo",
}

COLUMNAS_RESULTADOS = [
    "anio", "instancia", "fecha", "cargo",
    "distrito_id", "distrito", "seccion", "localidad", "circuito_id",
    "agrupacion", "tipo_registro", "votos", "archivo_origen",
]
COLUMNAS_METADATOS = [
    "anio", "instancia", "fecha", "distrito", "seccion", "localidad",
    "mesas", "electores", "archivo_origen",
]
COLUMNAS_NOMENCLADOR = ["anio", "circuito_id", "seccion", "localidad"]


def filas(hoja):
    """Devuelve las filas de una hoja como dicts, usando la fila 1 de nombres."""
    it = hoja.iter_rows(values_only=True)
    encabezado = [str(c).strip() if c is not None else "" for c in next(it)]
    for fila in it:
        if any(v is not None for v in fila):
            yield dict(zip(encabezado, fila))


def entero(v):
    return int(v) if isinstance(v, (int, float)) else 0


def parsear(archivo):
    m = re.match(r"(\d{4})_([A-Z]+)_", archivo.name)
    anio, instancia = m.group(1), m.group(2)
    comun = {
        "anio": anio, "instancia": instancia,
        "fecha": FECHAS.get((anio, instancia), ""), "cargo": CARGO,
        "distrito_id": DISTRITO_ID, "distrito": DISTRITO,
        "archivo_origen": archivo.name,
    }
    wb = openpyxl.load_workbook(archivo, read_only=True)

    # Circuito por localidad, para colgarlo de cada fila de resultados.
    nomenclador, circuito_de = [], {}
    for f in filas(wb["Nomenclador Circuito-Localidad"]):
        clave = (f["Departamento"], f["Localidad"])
        circuito_de[clave] = str(f["Circuito"]).strip()
        nomenclador.append({
            "anio": anio, "circuito_id": circuito_de[clave],
            "seccion": f["Departamento"], "localidad": f["Localidad"],
        })

    resultados = []
    for f in filas(wb["Votos por Localidad"]):
        clave = (f["Departamento"], f["Localidad"])
        resultados.append({
            **comun, "seccion": f["Departamento"], "localidad": f["Localidad"],
            "circuito_id": circuito_de.get(clave, ""),
            "agrupacion": f["Agrupacion_Politica"],
            "tipo_registro": "agrupacion", "votos": entero(f["Votos"]),
        })

    for f in filas(wb["Totales por Tipo de Voto"]):
        clave = (f["Departamento"], f["Localidad"])
        for col, tipo in TIPOS_VOTO.items():
            if col not in f:
                continue
            resultados.append({
                **comun, "seccion": f["Departamento"],
                "localidad": f["Localidad"],
                "circuito_id": circuito_de.get(clave, ""),
                "agrupacion": col, "tipo_registro": tipo,
                "votos": entero(f[col]),
            })

    metadatos = [{
        "anio": anio, "instancia": instancia, "fecha": comun["fecha"],
        "distrito": DISTRITO, "seccion": f["Departamento"],
        "localidad": f["Localidad"], "mesas": entero(f["Mesas"]),
        "electores": entero(f["Electores"]), "archivo_origen": archivo.name,
    } for f in filas(wb["Electores y Mesas"])]

    wb.close()
    return resultados, metadatos, nomenclador


def verificar(resultados, archivo):
    """Por localidad, las agrupaciones deben sumar el total de POSITIVO."""
    suma, positivo = {}, {}
    for f in resultados:
        clave = (f["seccion"], f["localidad"])
        if f["tipo_registro"] == "agrupacion":
            suma[clave] = suma.get(clave, 0) + f["votos"]
        elif f["tipo_registro"] == "positivo":
            positivo[clave] = f["votos"]
    avisos = []
    for clave, esperado in positivo.items():
        if suma.get(clave, 0) != esperado:
            avisos.append(f"{archivo}: {clave[1]} suma {suma.get(clave, 0):,} "
                          f"!= POSITIVO {esperado:,}")
    return avisos


def escribir(nombre, filas_datos, columnas):
    with open(SALIDA / nombre, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=columnas)
        w.writeheader()
        w.writerows(filas_datos)
    print(f"-> datos/procesados/{nombre} ({len(filas_datos)} filas)")


def main():
    archivos = sorted(CRUDOS.glob("*.xlsx"))
    if not archivos:
        sys.exit(f"no hay .xlsx en {CRUDOS}")

    resultados, metadatos, nomenclador, avisos = [], [], [], []
    for archivo in archivos:
        res, met, nom = parsear(archivo)
        avisos += verificar(res, archivo.name)
        resultados += res
        metadatos += met
        nomenclador += nom
        locs = len({(f["seccion"], f["localidad"]) for f in met})
        print(f"  {archivo.name[:46]:46} {len(res):>5} filas, {locs} localidades")

    SALIDA.mkdir(parents=True, exist_ok=True)
    escribir("resultados_localidad.csv", resultados, COLUMNAS_RESULTADOS)
    escribir("metadatos_localidad.csv", metadatos, COLUMNAS_METADATOS)
    # El nomenclador se repite en cada archivo del mismo anio: se deduplica.
    unicos = {tuple(n[c] for c in COLUMNAS_NOMENCLADOR) for n in nomenclador}
    escribir("nomenclador_circuito_localidad.csv",
             [dict(zip(COLUMNAS_NOMENCLADOR, t)) for t in sorted(unicos)],
             COLUMNAS_NOMENCLADOR)

    if avisos:
        print("\nControles de consistencia:")
        for a in avisos:
            print("  !", a)
    else:
        print("\nControles de consistencia: OK en todos los archivos.")


if __name__ == "__main__":
    main()
