#!/usr/bin/env python3
"""
Población 2022 de las localidades del análisis, a partir del Censo 2022 (INDEC).

Fuente: «Censo Nacional de Población, Hogares y Viviendas 2022», base agregada a nivel de
radio censal (datos.gob.ar, dataset 48, archivo `82-santa-fe-2022.zip`).
Método: la población de cada radio (suma de PERSONA_P02) se asigna al gobierno local que
informa VIVIENDA_CODGL para ese radio. En Santa Fe ningún radio mezcla gobiernos locales,
así que la asignación es exacta. La suma provincial (3.519.059) es la población en viviendas
particulares: queda por debajo del total publicado por INDEC porque no incluye viviendas
colectivas ni personas en situación de calle.

Si el equipo cuenta con la tabla oficial de población por localidad, reemplazar
`datos/referencia/poblacion_localidades_censo2022.csv` conserva todo el resto del proceso.

Salida: datos/referencia/poblacion_localidades_censo2022.csv

Uso: python3 scripts/construir_poblacion_censo2022.py [ruta_del_zip]   (si falta, se descarga)
"""
import collections
import csv
import io
import sys
import unicodedata
import urllib.request
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
URL = "https://infra.datos.gob.ar/catalog/indec/dataset/48/distribution/48.21/download/82-santa-fe-2022.zip"
DEST = RAIZ / "datos" / "referencia" / "poblacion_localidades_censo2022.csv"
META = RAIZ / "datos" / "procesados" / "metadatos_localidad.csv"
DEPTOS = {"Castellanos": "021", "Las Colonias": "070", "San Martín": "126"}


def norm(s):
    s = "".join(c for c in unicodedata.normalize("NFD", s.lower()) if unicodedata.category(c) != "Mn")
    return " ".join(s.split())


def abrir_zip():
    if len(sys.argv) > 1:
        return zipfile.ZipFile(sys.argv[1])
    print("descargando", URL)
    return zipfile.ZipFile(io.BytesIO(urllib.request.urlopen(URL, timeout=300).read()))


def main():
    z = abrir_zip()
    leer = lambda n: csv.DictReader(io.TextIOWrapper(z.open(n), encoding="utf-8-sig"))
    pob = collections.defaultdict(int)
    for r in leer("82-santa-fe-2022-persona.csv"):
        if r["cod_variable"] == "PERSONA_P02":
            pob[r["codigo"]] += int(r["cantidad"])
    gl = collections.defaultdict(dict)
    nom, dep = {}, {}
    for r in leer("82-santa-fe-2022-vivienda.csv"):
        if r["cod_variable"] == "VIVIENDA_CODGL":
            gl[r["codigo"]][r["cod_categoria"]] = int(r["cantidad"])
            nom[r["cod_categoria"]], dep[r["cod_categoria"]] = r["categoria"], r["cod_dep"]
    if any(len(v) > 1 for v in gl.values()):
        sys.exit("hay radios con más de un gobierno local: hace falta prorratear")
    poblacion = collections.defaultdict(int)
    for radio, p in pob.items():
        for c in gl.get(radio, {}):
            poblacion[c] += p
    print("población en viviendas particulares, Santa Fe:", f"{sum(pob.values()):,}".replace(",", "."))

    locs = sorted({(r["seccion"], r["localidad"]) for r in csv.DictReader(open(META, encoding="utf-8"))})
    por_nombre = collections.defaultdict(list)
    for c, n in nom.items():
        por_nombre[(dep[c], norm(n))].append(c)
    filas, error = [], []
    for seccion, localidad in locs:
        cods = por_nombre.get((DEPTOS[seccion], norm(localidad)), [])
        if len(cods) != 1:
            error.append((seccion, localidad, cods)); continue
        c = cods[0]
        filas.append([seccion, localidad, c, nom[c], poblacion[c],
                      "Censo 2022 (INDEC), radios censales; viviendas particulares"])
    if error:
        sys.exit(f"localidades sin gobierno local único: {error}")
    DEST.parent.mkdir(parents=True, exist_ok=True)
    with open(DEST, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["departamento", "localidad", "codigo_gobierno_local", "nombre_censo", "poblacion_2022", "fuente"])
        w.writerows(filas)
    print(f"{len(filas)} localidades -> {DEST.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
