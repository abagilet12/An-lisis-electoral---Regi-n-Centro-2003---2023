#!/usr/bin/env python3
"""
Chequeo de la población del Censo 2022 usada en «El voto según el tamaño del lugar».

Tres contrastes
  1. Contra cifras oficiales conocidas: total provincial y cinco localidades (INDEC, resultados definitivos,
     según las notas de prensa citadas en docs/VERIFICACION_POBLACION.md).
  2. Contra el padrón electoral: electores 2023 de cada localidad (suma de sus circuitos, según
     datos/referencia/circuito_localidad.csv) frente a la población de 16 años o más del mismo censo.
     Un cociente cercano a 1 confirma a la vez la población y la asignación de circuitos a localidades.
  3. Contra las 30 localidades con resultados propios: electores de la fuente por localidad frente a los
     reconstruidos desde circuitos.

Salida: datos/procesados/verificacion_poblacion.csv (una fila por localidad) e informe por pantalla.

Uso: python3 scripts/verificar_poblacion_censo.py [82-santa-fe-2022.zip]
"""
import collections
import csv
import io
import statistics
import sys
import urllib.request
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
REF, PROC = RAIZ / "datos" / "referencia", RAIZ / "datos" / "procesados"
URL = "https://infra.datos.gob.ar/catalog/indec/dataset/48/distribution/48.21/download/82-santa-fe-2022.zip"
nz = lambda c: c.lstrip("0")

# cifras oficiales (INDEC, definitivos) difundidas en prensa; ver docs/VERIFICACION_POBLACION.md
OFICIAL = {"Rosario": 1029619, "Santa Fe": 403878, "Rafaela": 101733, "Reconquista": 87965, "Venado Tuerto": 82757}
OFICIAL_PROV = 3544908

z = zipfile.ZipFile(sys.argv[1]) if len(sys.argv) > 1 else zipfile.ZipFile(io.BytesIO(urllib.request.urlopen(URL, timeout=300).read()))
leer = lambda n: csv.DictReader(io.TextIOWrapper(z.open(n), encoding="utf-8-sig"))
glr = {}
for r in leer("82-santa-fe-2022-vivienda.csv"):
    if r["cod_variable"] == "VIVIENDA_CODGL":
        glr[r["codigo"]] = r["cod_categoria"]
pob16 = collections.defaultdict(int); pob = collections.defaultdict(int)
for r in leer("82-santa-fe-2022-persona.csv"):
    if r["cod_variable"] == "PERSONA_EDAD":
        n = int(r["cantidad"]); edad = int(r["categoria"]) if r["categoria"].isdigit() else None
        gl = glr[r["codigo"]]
        pob[gl] += n
        if edad is not None and edad >= 16:
            pob16[gl] += n

gles = {r["codigo_gobierno_local"]: (r["gobierno_local"], int(r["poblacion_2022"])) for r in csv.DictReader(open(REF / "poblacion_gobiernos_locales_censo2022.csv", encoding="utf-8"))}
asig = {nz(r["circuito"]): r for r in csv.DictReader(open(REF / "circuito_localidad.csv", encoding="utf-8")) if r["capa"] == "2023"}
electores = collections.defaultdict(int)
for r in csv.DictReader(open(PROC / "nomenclador_circuitos_2023.csv", encoding="utf-8")):
    a = asig.get(nz(r["circuito_id"]))
    if a:
        electores[a["codigo_gobierno_local"]] += int(r["electores"])

# 1. cifras oficiales
tot = sum(v[1] for v in gles.values())
print(f"Total provincial: {tot:,} (viviendas particulares) contra {OFICIAL_PROV:,} oficial: {100*(tot-OFICIAL_PROV)/OFICIAL_PROV:+.2f} %".replace(",", "."))
for n, o in OFICIAL.items():
    ours = next(v[1] for v in gles.values() if v[0] == n)
    print(f"  {n:14} {ours:>9,} contra {o:>9,}: {100*(ours-o)/o:+.2f} %".replace(",", "."))

# 2. electores / población 16+
filas = []
for gl, (n, p) in gles.items():
    e = electores.get(gl, 0)
    if e:
        filas.append([gl, n, p, pob16[gl], e, round(e / pob16[gl], 3) if pob16[gl] else ""])
rat = [f[5] for f in filas if f[5] != ""]
print(f"\nElectores 2023 / población de 16+: mediana {statistics.median(rat):.2f}; "
      f"percentiles 5 y 95: {sorted(rat)[int(.05*len(rat))]:.2f} y {sorted(rat)[int(.95*len(rat))]:.2f}; {len(rat)} localidades")
print(f"Provincia: {sum(f[4] for f in filas):,} electores / {sum(f[3] for f in filas):,} habitantes de 16+ = "
      f"{sum(f[4] for f in filas)/sum(f[3] for f in filas):.3f}".replace(",", "."))
sospechosas = sorted([f for f in filas if f[5] != "" and (f[5] < 0.6 or f[5] > 1.25)], key=lambda f: -f[4])
print("Fuera de 0,6 a 1,25:", [(f[1], f[4], f[3], f[5]) for f in sospechosas[:12]])
peso = sum(f[4] for f in sospechosas) / sum(f[4] for f in filas)
print(f"  esas {len(sospechosas)} localidades reúnen el {100*peso:.1f} % de los electores")
with open(PROC / "verificacion_poblacion.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh, lineterminator="\n")
    w.writerow(["codigo_gobierno_local", "localidad", "poblacion_2022", "poblacion_16_y_mas", "electores_2023", "electores_sobre_poblacion_16_y_mas"])
    w.writerows(sorted(filas, key=lambda f: -f[4]))
