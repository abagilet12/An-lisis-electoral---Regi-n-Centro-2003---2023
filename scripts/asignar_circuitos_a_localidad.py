#!/usr/bin/env python3
"""
Asigna cada circuito electoral a su localidad (gobierno local) y le da la población del Censo 2022.

Por qué: solo hay resultados «por localidad» para 30 localidades, pero hay resultados por circuito
para toda la provincia y las 12 instancias. Cruzando la cartografía de circuitos con los radios
censales se obtiene, para cada circuito, el gobierno local en el que cae. Sumando los circuitos de
un mismo gobierno local se reconstruyen los resultados por localidad de toda la provincia.

Método
  1. Población de cada radio censal: POB_TOT_P del shapefile de radios (INDEC, Censo 2022).
  2. Gobierno local de cada radio: VIVIENDA_CODGL del CSV por radio (ningún radio mezcla gobiernos
     locales). Población de cada gobierno local = suma de sus radios.
  3. Para cada capa de circuitos (datos/geo/circuitos/santafe_circuitos_<año>_reconstruido.geojson)
     se intersecta cada circuito con los radios; la población que aporta un radio es la fracción de
     su superficie dentro del circuito por su población. El circuito se asigna al gobierno local que
     más población aporta.

  4. Donde existe el nomenclador circuito→localidad relevado a mano (datos/procesados/
     nomenclador_circuito_localidad.csv, 30 localidades), ese nomenclador prevalece sobre el cruce
     espacial. El cruce lo reproduce en 149 de 150 casos; el desacuerdo (circuito 01345 de 2023) se
     debe a la reconstrucción del polígono de un circuito subdividido entre 2023 y 2025.

Entradas  radios-censales-2022.zip y 82-santa-fe-2022.zip (datos.gob.ar, dataset 50 y 48); se
          descargan si no se pasan rutas.
Salidas   datos/referencia/poblacion_gobiernos_locales_censo2022.csv
          datos/referencia/circuito_localidad.csv   (capa, circuito, gobierno local, población, % del circuito)

Uso: python3 scripts/asignar_circuitos_a_localidad.py [radios.zip] [82-santa-fe-2022.zip]
"""
import collections
import csv
import io
import json
import sys
import tempfile
import unicodedata
import urllib.request
import zipfile
from pathlib import Path

import shapefile
from shapely.geometry import shape
from shapely.strtree import STRtree

RAIZ = Path(__file__).resolve().parent.parent
GEO = RAIZ / "datos" / "geo" / "circuitos"
REF = RAIZ / "datos" / "referencia"
URL_RADIOS = "https://infra.datos.gob.ar/catalog/indec/dataset/50/distribution/50.3/download/radios-censales-2022.zip"
URL_CENSO = "https://infra.datos.gob.ar/catalog/indec/dataset/48/distribution/48.21/download/82-santa-fe-2022.zip"
CAPAS = ["2003", "2007", "2011", "2015", "2019", "2023"]
DEPTOS = {"Castellanos": "021", "Las Colonias": "070", "San Martín": "126"}   # códigos INDEC


def norm(s):
    s = "".join(c for c in unicodedata.normalize("NFD", s.lower()) if unicodedata.category(c) != "Mn")
    return " ".join(s.split())


nz = lambda c: c.lstrip("0")


def zip_de(arg, url):
    if arg:
        return zipfile.ZipFile(arg)
    print("descargando", url)
    return zipfile.ZipFile(io.BytesIO(urllib.request.urlopen(url, timeout=600).read()))


def main():
    zr = zip_de(sys.argv[1] if len(sys.argv) > 1 else None, URL_RADIOS)
    zc = zip_de(sys.argv[2] if len(sys.argv) > 2 else None, URL_CENSO)

    # 1-2. gobierno local de cada radio y población por gobierno local
    nom, dep, glr = {}, {}, {}
    for r in csv.DictReader(io.TextIOWrapper(zc.open("82-santa-fe-2022-vivienda.csv"), encoding="utf-8-sig")):
        if r["cod_variable"] == "VIVIENDA_CODGL":
            if r["codigo"] in glr and glr[r["codigo"]] != r["cod_categoria"]:
                sys.exit(f"el radio {r['codigo']} mezcla gobiernos locales")
            glr[r["codigo"]] = r["cod_categoria"]
            nom[r["cod_categoria"]], dep[r["cod_categoria"]] = r["categoria"], r["departamento"]
    with tempfile.TemporaryDirectory() as tmp:
        zr.extractall(tmp)
        sf = shapefile.Reader(str(next(Path(tmp).glob("*.shp"))))
        radios = []
        for sr in sf.iterShapeRecords():
            rec = sr.record
            if not rec[1].startswith("82") or not rec[5]:
                continue
            geom = shape(sr.shape.__geo_interface__)
            if not geom.is_valid:
                geom = geom.buffer(0)
            radios.append((rec[0], int(rec[5]), geom))
    pob_gl = collections.defaultdict(int)
    for cod, p, _ in radios:
        pob_gl[glr[cod]] += p
    with open(REF / "poblacion_gobiernos_locales_censo2022.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["codigo_gobierno_local", "gobierno_local", "cod_departamento", "poblacion_2022"])
        for c in sorted(pob_gl, key=lambda c: -pob_gl[c]):
            w.writerow([c, nom[c], dep[c], pob_gl[c]])
    print(f"{len(pob_gl)} gobiernos locales; población {sum(pob_gl.values()):,}".replace(",", "."))

    # 3. circuitos × radios
    arbol = STRtree([g for _, _, g in radios])
    filas, resumen = [], {}
    for capa in CAPAS:
        gj = json.load(open(GEO / f"santafe_circuitos_{capa}_reconstruido.geojson", encoding="utf-8"))
        sin, partidos, n = 0, 0, 0
        for ft in gj["features"]:
            circ = shape(ft["geometry"])
            if not circ.is_valid:
                circ = circ.buffer(0)
            aporte = collections.defaultdict(float)
            area = collections.defaultdict(float)
            for i in arbol.query(circ):
                cod, p, g = radios[int(i)]
                inter = g.intersection(circ).area
                if inter <= 0 or g.area <= 0:
                    continue
                aporte[glr[cod]] += p * inter / g.area
                area[glr[cod]] += inter
            n += 1
            if not aporte:
                sin += 1; continue
            base = aporte if sum(aporte.values()) > 0 else area
            gl = max(base, key=base.get)
            tot = sum(base.values())
            if base[gl] / tot < 0.9:
                partidos += 1
            filas.append([capa, ft["properties"]["circuito"], gl, nom[gl], pob_gl[gl],
                          f"{100 * base[gl] / tot:.1f}", round(sum(aporte.values())), "espacial"])
        resumen[capa] = (n, sin, partidos)
    # 4. el nomenclador relevado a mano prevalece
    por_nombre = {(dep[c], norm(nom[c])): c for c in nom}
    cambios = []
    manual = {(r["anio"], nz(r["circuito_id"])): (r["seccion"], r["localidad"])
              for r in csv.DictReader(open(RAIZ / "datos" / "procesados" / "nomenclador_circuito_localidad.csv", encoding="utf-8"))}
    for f in filas:
        m = manual.get((f[0], nz(f[1])))
        if not m:
            continue
        gl = por_nombre[(DEPTOS[m[0]], norm(m[1]))]
        if gl != f[2]:
            cambios.append((f[0], f[1], f[3], nom[gl]))
            f[2], f[3], f[4] = gl, nom[gl], pob_gl[gl]
        f[7] = "nomenclador" if gl == f[2] else f[7]
    print("corregidos con el nomenclador a mano:", cambios or "ninguno")
    with open(REF / "circuito_localidad.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["capa", "circuito", "codigo_gobierno_local", "localidad", "poblacion_localidad_2022",
                    "pct_poblacion_del_circuito_en_la_localidad", "poblacion_estimada_circuito", "origen"])
        w.writerows(filas)
    for capa, (n, sin, partidos) in resumen.items():
        print(f"capa {capa}: {n} circuitos · sin radios {sin} · con menos de 90 % de su población en una sola localidad {partidos}")


if __name__ == "__main__":
    main()
