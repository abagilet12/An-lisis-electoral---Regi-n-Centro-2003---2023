#!/usr/bin/env python3
"""
Aísla y controla los votos de la derecha libertaria (docs/CRITERIO_DERECHA_LIBERTARIA.md).

Criterio: antes de 2023 la familia se llama «Derecha libertaria»; desde 2023 todo voto de
esa derecha, el de La Libertad Avanza incluido, se computa en la familia «La Libertad
Avanza». Este script no cambia ningún dato: lo verifica y deja a la vista cada voto.

Controles
  1. Ninguna fila de 2023 en adelante tiene la familia «Derecha libertaria», y ninguna
     anterior a 2023 tiene la familia «La Libertad Avanza» (en serie_homologada.csv).
  2. Conservación: los votos de las dos familias suman lo mismo que las etiquetas
     originales de ese linaje (Unite en 2019; La Libertad Avanza en 2023), nivel por nivel.
  3. salida/datos_analisis.json (por departamento) coincide con serie_homologada.csv
     (por circuito) para las dos familias en cada elección.
  4. Ninguna otra etiqueta anterior a 2023 menciona «libert», «Espert», «Unite» o «Milei»
     sin estar clasificada en la familia (se informa, no se corrige: es decisión de investigación).

Salida: datos/procesados/derecha_libertaria_pre2023.csv (una fila por elección anterior a
2023, etiqueta original y departamento; solo votos de la familia «Derecha libertaria»).
"""
import collections
import csv
import json
import sys
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PROC = RAIZ / "datos" / "procesados"
FAM_PRE, FAM_POST = "Derecha libertaria", "La Libertad Avanza"
LINAJE = {("2019", "Unite (Espert)"): FAM_PRE, ("2023", "La Libertad Avanza"): FAM_POST}

serie = list(csv.DictReader(open(PROC / "serie_homologada.csv", encoding="utf-8")))
error = []

# 1. el criterio se cumple fila por fila
for r in serie:
    if int(r["anio"]) >= 2023 and r["familia"] == FAM_PRE:
        error.append(f"{r['anio']} {r['instancia']}: «{FAM_PRE}» desde 2023 ({r['agrupacion_original']})")
    if int(r["anio"]) < 2023 and r["familia"] == FAM_POST:
        error.append(f"{r['anio']} {r['instancia']}: «{FAM_POST}» antes de 2023 ({r['agrupacion_original']})")

# 2. conservación por (elección, nivel, universo)
fam = collections.defaultdict(int)
linaje = collections.defaultdict(int)
for r in serie:
    k = (r["anio"], r["instancia"], r["nivel"], r["universo"])
    v = int(float(r["votos"]))
    if r["familia"] in (FAM_PRE, FAM_POST):
        fam[k] += v
    if (r["anio"], r["agrupacion_homologada"]) in LINAJE:
        linaje[k] += v
if fam != linaje:
    for k in sorted(set(fam) | set(linaje)):
        if fam.get(k) != linaje.get(k):
            error.append(f"conservación {k}: familias {fam.get(k)} vs etiquetas {linaje.get(k)}")

# 3. el dato por departamento coincide con el dato por circuito
da = json.loads((RAIZ / "salida" / "datos_analisis.json").read_text(encoding="utf-8"))
circ = collections.defaultdict(int)
for r in serie:
    if r["nivel"] == "circuito" and r["familia"] in (FAM_PRE, FAM_POST):
        circ[(f"{r['anio']}-{r['instancia']}", r["familia"])] += int(float(r["votos"]))
dep = collections.defaultdict(int)
for clave, deptos in da["datos"].items():
    for d in deptos.values():
        for f in (FAM_PRE, FAM_POST):
            dep[(clave, f)] += d["v"].get(f, 0)
for k in sorted(set(circ) | set(dep)):
    if circ.get(k, 0) != dep.get(k, 0):
        error.append(f"circuito vs departamento {k}: {circ.get(k, 0)} vs {dep.get(k, 0)}")

# 4. etiquetas sospechosas fuera de la familia
hom = list(csv.DictReader(open(RAIZ / "datos/referencia/homologacion_agrupaciones.csv", encoding="utf-8")))
def sin_tildes(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn").lower()


# «Unión y Libertad» / «Justicia, Unión y Libertad» son nombres del peronismo de Rodríguez Saá,
# no de la derecha libertaria: se excluyen del aviso.
aviso = sorted({(r["anio"], r["agrupacion_original"], r["familia"]) for r in hom
                if int(r["anio"]) < 2023 and r["familia"] != FAM_PRE
                and any(s in sin_tildes(r["agrupacion_original"]) for s in ("libert", "espert", "unite", "milei"))
                and "union y libertad" not in sin_tildes(r["agrupacion_original"])})

# salida aislada: solo la familia «Derecha libertaria», antes de 2023, nivel circuito sumado a departamento
salida = collections.defaultdict(int)
for r in serie:
    if r["nivel"] == "circuito" and r["familia"] == FAM_PRE and int(r["anio"]) < 2023:
        salida[(r["anio"], r["instancia"], r["agrupacion_original"], r["agrupacion_homologada"], r["seccion"])] += int(float(r["votos"]))
destino = PROC / "derecha_libertaria_pre2023.csv"
with open(destino, "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh, lineterminator="\n")
    w.writerow(["anio", "instancia", "agrupacion_original", "agrupacion_homologada", "familia", "departamento", "votos"])
    for k in sorted(salida):
        w.writerow([*k[:4], FAM_PRE, k[4], salida[k]])

print("Votos de la familia «Derecha libertaria» (solo antes de 2023), total provincial por circuitos:")
for (clave, f), v in sorted(circ.items()):
    if f == FAM_PRE:
        print(f"  {clave:14} {v:>9,}".replace(",", "."))
print("Votos de la familia «La Libertad Avanza» (2023 en adelante):")
for (clave, f), v in sorted(circ.items()):
    if f == FAM_POST:
        print(f"  {clave:14} {v:>9,}".replace(",", "."))
print("Etiquetas anteriores a 2023 con rasgos libertarios fuera de la familia:", aviso or "ninguna")
print("Archivo:", destino.relative_to(RAIZ), f"({len(salida)} filas)")
if error:
    print("\nERRORES:"); [print(" ", e) for e in error]; sys.exit(1)
print("\nControles 1-3: sin diferencias.")
