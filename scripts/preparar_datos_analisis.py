#!/usr/bin/env python3
"""
Prepara el dataset compacto que consume la página de análisis.

Agrega los resultados por circuito a **departamento y familia política**, que
es el nivel donde una serie de veinte años se lee sin ruido. El circuito
queda para el mapa; acá interesa la tendencia.

Dos normalizaciones necesarias, ambas verificadas:

1. **Mayúsculas.** Los archivos de 2023 traen el departamento en mayúsculas y
   los de PolAr en capitalización normal. Sin unificar, "ROSARIO" y "Rosario"
   cuentan como departamentos distintos.

2. **Sub-unidades de 2011.** Ese año la provincia viene partida en 22 unidades
   en vez de 19. Las tres extra son subdivisiones de dos departamentos:
   "Rosario Barr.", "Rosario Camp." y "La Capital Camp.". Fusionándolas con su
   departamento, 2011 queda comparable con el resto de la serie. Es decir: la
   anomalía que veníamos arrastrando se resuelve, no es un límite del dato.

Salida: salida/datos_analisis.json
"""
import collections
import csv
import json
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PROC = RAIZ / "datos" / "procesados"
TABLA_HOM = RAIZ / "datos" / "referencia" / "homologacion_agrupaciones.csv"
DESTINO = RAIZ / "salida" / "datos_analisis.json"

FUENTES = ["resultados_circuito_polar.csv", "2023_PASO_circuito.csv",
           "2023_GENERAL_circuito.csv", "2023_BALOTAJE_circuito.csv"]
NO_POSITIVOS = ("blancos", "nulos", "impugnados", "recurridos", "comando")
ORDEN = {"PASO": 0, "GENERAL": 1, "BALOTAJE": 2}
ARTICULOS = {"de", "del", "la", "las", "los", "y"}

FECHAS = {
    ("2003", "GENERAL"): "27/04/2003", ("2007", "GENERAL"): "28/10/2007",
    ("2011", "PASO"): "14/08/2011", ("2011", "GENERAL"): "23/10/2011",
    ("2015", "PASO"): "09/08/2015", ("2015", "GENERAL"): "25/10/2015",
    ("2015", "BALOTAJE"): "22/11/2015",
    ("2019", "PASO"): "11/08/2019", ("2019", "GENERAL"): "27/10/2019",
    ("2023", "PASO"): "13/08/2023", ("2023", "GENERAL"): "22/10/2023",
    ("2023", "BALOTAJE"): "19/11/2023",
}

# Variantes de nombre que designan el mismo departamento.
ALIAS = {"9 DE JULIO": "Nueve de Julio", "NUEVE DE JULIO": "Nueve de Julio",
         "ROSARIO BARR.": "Rosario", "ROSARIO CAMP.": "Rosario",
         "LA CAPITAL CAMP.": "La Capital"}


def sin_tildes(s):
    d = unicodedata.normalize("NFD", s.upper())
    return "".join(c for c in d if unicodedata.category(c) != "Mn")


def normalizar_depto(s):
    s = (s or "").strip()
    alias = ALIAS.get(sin_tildes(s))
    if alias:
        return alias
    palabras = s.split()
    return " ".join(
        p.capitalize() if i == 0 or p.lower() not in ARTICULOS else p.lower()
        for i, p in enumerate(palabras))


def padron_por_circuito():
    """Padron y mesas de cada circuito, por anio.

    Los archivos de circuito de 2023 no llevan esas columnas —se generaron
    aparte, en el nomenclador—, asi que sin esto el padron de 2023 queda en
    cero y arrastra la participacion.
    """
    tabla = {}
    for ruta in PROC.glob("nomenclador_circuitos_*.csv"):
        for r in csv.DictReader(open(ruta, encoding="utf-8")):
            tabla[(r["anio_referencia"], r["circuito_id"])] = (
                int(r["electores"] or 0), int(r["mesas"] or 0))
    return tabla


def main():
    hom = {(r["anio"], r["instancia"], r["agrupacion_original"].strip()): r
           for r in csv.DictReader(open(TABLA_HOM, encoding="utf-8"))}
    nomen = padron_por_circuito()

    votos = collections.defaultdict(int)
    otros = collections.defaultdict(int)
    padron = collections.defaultdict(int)
    mesas = collections.defaultdict(int)
    vistos = set()

    for nombre in FUENTES:
        ruta = PROC / nombre
        if not ruta.exists():
            continue
        for r in csv.DictReader(open(ruta, encoding="utf-8")):
            clave = (r["anio"], r["instancia"])
            depto = normalizar_depto(r.get("seccion"))

            # Padron y mesas se cuentan una vez por circuito, no por fila.
            unidad = (clave, r["circuito_id"])
            if unidad not in vistos:
                vistos.add(unidad)
                e, m = nomen.get((r["anio"], r["circuito_id"]), (0, 0))
                padron[(*clave, depto)] += int(float(r.get("electores") or e))
                mesas[(*clave, depto)] += int(float(r.get("mesas") or m))

            tipo, cantidad = r["tipo_registro"], int(float(r["votos"]))
            if tipo == "agrupacion":
                h = hom.get((*clave, r["agrupacion"].strip()))
                votos[(*clave, depto, h["familia"] if h else "Otros")] += cantidad
            elif tipo in NO_POSITIVOS:
                otros[(*clave, depto, tipo)] += cantidad

    elecciones = sorted({(a, i) for a, i, _, _ in votos},
                        key=lambda x: (x[0], ORDEN[x[1]]))
    familias = sorted({f for _, _, _, f in votos})
    deptos = sorted({d for _, _, d, _ in votos})

    salida = {
        "elecciones": [{"anio": a, "instancia": i,
                        "fecha": FECHAS.get((a, i), ""), "clave": f"{a}-{i}"}
                       for a, i in elecciones],
        "familias": familias, "departamentos": deptos, "datos": {},
    }
    for a, i in elecciones:
        k = f"{a}-{i}"
        salida["datos"][k] = {}
        for d in deptos:
            v = {f: votos[(a, i, d, f)] for f in familias
                 if votos.get((a, i, d, f))}
            if not v:
                continue
            salida["datos"][k][d] = {
                "v": v,
                "n": {t: otros[(a, i, d, t)] for t in NO_POSITIVOS
                      if otros.get((a, i, d, t))},
                "p": padron[(a, i, d)], "m": mesas[(a, i, d)],
            }

    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    texto = json.dumps(salida, ensure_ascii=False, separators=(",", ":"))
    DESTINO.write_text(texto, encoding="utf-8")

    print(f"{len(elecciones)} elecciones · {len(deptos)} departamentos · "
          f"{len(familias)} familias · {len(texto)/1024:.0f} KB")
    for a, i in elecciones:
        n = len(salida["datos"][f"{a}-{i}"])
        marca = "" if n == len(deptos) else f"   <- {n} departamentos"
        print(f"  {a} {i:9}{marca}")


if __name__ == "__main__":
    main()
