#!/usr/bin/env python3
"""
Ordena el registro de candidaturas presidenciales de la DINE (generales 1983-2023)
por fórmula.

Entrada: datos/crudos/dine_candidaturas/Candidaturas_Presidenciales_1983-2023.xlsx
Salida:  datos/referencia/formulas_presidenciales_1983_2023.csv

El Excel trae una fila por candidato y por agrupación. Una misma fórmula aparece
repetida bajo cada partido o alianza que la presentó (Menem 1995 figura cuatro
veces, Sobisch 2007 cuatro). Aquí se junta cada fórmula en una fila y se listan
las etiquetas bajo las que se presentó.
"""
import csv
import collections
import re
import unicodedata
from pathlib import Path

import openpyxl

RAIZ = Path(__file__).resolve().parent.parent
ENTRADA = RAIZ / "datos" / "crudos" / "dine_candidaturas" / "Candidaturas_Presidenciales_1983-2023.xlsx"
SALIDA = RAIZ / "datos" / "referencia" / "formulas_presidenciales_1983_2023.csv"


def limpio(s):
    return re.sub(r"\s+", " ", str(s or "")).strip()


def clave(s):
    s = unicodedata.normalize("NFD", limpio(s)).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z ]", "", s)


def main():
    ws = openpyxl.load_workbook(ENTRADA, read_only=True, data_only=True)["Hoja1"]
    it = ws.iter_rows(values_only=True)
    cab = next(it)
    filas = [dict(zip(cab, r)) for r in it if r[0]]
    por_agr = collections.defaultdict(dict)
    for r in filas:
        k = (r["Año"], limpio(r["Agrupación Política"]), r["Número Agrupación Política"])
        por_agr[k]["pres" if r["Cargo"].startswith("Pres") else "vice"] = limpio(r["Nombre en Boleta"])
        por_agr[k]["tipo"] = r["Elección Tipo"]
    formulas = []
    for (anio, etiqueta, num), d in por_agr.items():
        tp, tv = set(clave(d["pres"]).split()), set(clave(d["vice"]).split())
        for e in formulas:
            # misma fórmula: mismo año, apellido en común del presidente y del vice
            # (la fuente escribe distinto un mismo nombre: «Carlos Ruckauf» y «Carlos Federico Ruckauf»)
            if e["anio"] == anio and len(tp & e["tp"]) >= 2 and len(tv & e["tv"]) >= 1:
                e["etiquetas"].append(etiqueta)
                break
        else:
            formulas.append({"anio": anio, "presidente": d["pres"], "vice": d["vice"], "tp": tp, "tv": tv,
                             "etiquetas": [etiqueta]})
    with open(SALIDA, "w", newline="", encoding="utf8") as fh:
        w = csv.writer(fh)
        w.writerow(["anio", "tipo_eleccion", "presidente", "vicepresidente", "cantidad_de_etiquetas", "etiquetas"])
        for e in sorted(formulas, key=lambda e: (e["anio"], e["presidente"])):
            w.writerow([e["anio"], "Generales", e["presidente"], e["vice"], len(e["etiquetas"]), " | ".join(e["etiquetas"])])
    print(len(filas), "filas;", len(formulas), "fórmulas")


if __name__ == "__main__":
    main()
