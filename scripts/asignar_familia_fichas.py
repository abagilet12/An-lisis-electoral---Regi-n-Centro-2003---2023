#!/usr/bin/env python3
"""
Asigna a cada etiqueta de salida/datos_fichas.json su familia política (campo `f`),
para que las pestañas «Elecciones» y «Partidos» usen el color de la familia.

La familia sale de datos/referencia/homologacion_agrupaciones.csv, por elección y por
nombre original de la etiqueta (sin tildes, sin «alianza», sin signos). Una etiqueta
que no figura en la homologación queda con familia «Otros» (gris), según
docs/CRITERIOS_COLOR.md. Se puede correr las veces que haga falta.

Uso: python3 scripts/asignar_familia_fichas.py [datos_fichas.json]
"""
import csv
import json
import re
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DATOS = Path(sys.argv[1]) if len(sys.argv) > 1 else RAIZ / "salida" / "datos_fichas.json"
HOMOL = RAIZ / "datos" / "referencia" / "homologacion_agrupaciones.csv"


def norm(s):
    s = "".join(c for c in unicodedata.normalize("NFD", str(s)) if unicodedata.category(c) != "Mn").lower()
    s = re.sub(r"[^a-z0-9]+", " ", s).strip()
    return re.sub(r"^(alianza|al) ", "", s)


H = defaultdict(dict)
for r in csv.DictReader(open(HOMOL, encoding="utf-8")):
    H[f"{r['anio']}-{r['instancia']}"][norm(r["agrupacion_original"])] = r["familia"]

d = json.loads(DATOS.read_text(encoding="utf-8"))
sin = []
for cl, pts in d["pt"].items():
    for p in pts:
        f = None
        for o in [*p.get("o", []), p["n"]]:
            f = f or H[cl].get(norm(o))
        if not f:
            sin.append((cl, p["n"]))
        p["f"] = f or "Otros"
DATOS.write_text(json.dumps(d, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print(f"{sum(len(v) for v in d['pt'].values())} etiquetas; sin familia: {sin or 'ninguna'}")
