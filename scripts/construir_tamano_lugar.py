#!/usr/bin/env python3
"""
El voto según el tamaño del lugar (localidades × población del Censo 2022).

Entradas
  datos/procesados/serie_homologada.csv           resultados por localidad con familia política
  datos/referencia/poblacion_localidades_censo2022.csv   población 2022 por localidad
  datos/referencia/escala_tamano_lugar.csv        escala demográfica (Rural … Ciudad grande)
  datos/procesados/metadatos_localidad.csv        electores por localidad (para el control)
  datos/procesados/serie_homologada.csv (nivel provincia/circuito) para el peso de la muestra

Salidas
  datos/procesados/tamano_lugar.csv               localidad × elección × familia, con población y categoría
  datos/procesados/tamano_lugar_correlaciones.csv correlación población-voto por elección y familia
  salida/datos_tamano_lugar.json                  versión compacta para el tablero

Controles (se imprimen y detienen el proceso si fallan los de tipo ERROR)
  1. cada localidad tiene población y una única categoría;
  2. cada elección tiene las 30 localidades y sus votos suman lo mismo que serie_localidad.csv;
  3. relación electores/población dentro de lo esperable (0,5 a 0,95);
  4. cuántas localidades hay por categoría y qué parte de la provincia representan.
"""
import collections
import csv
import json
import math
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PROC = RAIZ / "datos" / "procesados"
REF = RAIZ / "datos" / "referencia"
ORDEN = {"PASO": 0, "GENERAL": 1, "BALOTAJE": 2}


def leer(p):
    return list(csv.DictReader(open(p, encoding="utf-8")))


escala = [(int(r["orden"]), r["categoria"], int(r["desde"]), int(r["hasta"]) if r["hasta"] else None)
          for r in leer(REF / "escala_tamano_lugar.csv")]


def categoria(p):
    for _, nombre, d, h in escala:
        if p >= d and (h is None or p <= h):
            return nombre
    raise ValueError(p)


pob = {(r["departamento"], r["localidad"]): int(r["poblacion_2022"])
       for r in leer(REF / "poblacion_localidades_censo2022.csv")}
serie = [r for r in leer(PROC / "serie_homologada.csv") if r["nivel"] == "localidad"]
error = []

# votos por (elección, localidad, familia)
v = collections.defaultdict(int)
for r in serie:
    v[(f"{r['anio']}-{r['instancia']}", r["seccion"], r["localidad"], r["familia"])] += int(float(r["votos"]))
claves = sorted({k[0] for k in v}, key=lambda c: (c[:4], ORDEN[c[5:]]))
locs = sorted(pob, key=lambda k: (k[0], k[1]))
familias = sorted({k[3] for k in v})

# 1. población y categoría
for k in locs:
    if k not in pob or not pob[k]:
        error.append(f"sin población: {k}")
# 2. cobertura y conservación
sl = collections.defaultdict(int)
for r in leer(PROC / "serie_localidad.csv"):
    if r["tipo_registro"] == "agrupacion":
        sl[f"{r['anio']}-{r['instancia']}"] += int(float(r["votos"]))
for c in claves:
    presentes = {(k[1], k[2]) for k in v if k[0] == c}
    if presentes != set(locs):
        error.append(f"{c}: faltan localidades {set(locs) - presentes}")
    tot = sum(x for k, x in v.items() if k[0] == c)
    if sl and tot != sl.get(c, tot):
        error.append(f"{c}: {tot} votos por familia vs {sl[c]} en serie_localidad.csv")

# 3. electores / población
el = {}
for r in leer(PROC / "metadatos_localidad.csv"):
    if r["anio"] == "2023" and r["instancia"] == "GENERAL":
        el[(r["seccion"], r["localidad"])] = int(r["electores"])
raros = [(k, round(el[k] / pob[k], 2)) for k in locs if k in el and not 0.5 <= el[k] / pob[k] <= 0.95]

# salida larga
out = PROC / "tamano_lugar.csv"
with open(out, "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh, lineterminator="\n")
    w.writerow(["clave", "departamento", "localidad", "poblacion_2022", "categoria", "familia", "votos"])
    for (c, d, l, f), x in sorted(v.items(), key=lambda t: (t[0][0], t[0][1], t[0][2], t[0][3])):
        w.writerow([c, d, l, pob[(d, l)], categoria(pob[(d, l)]), f, x])


def rangos(x):
    s = sorted(range(len(x)), key=lambda i: x[i]); r = [0.0] * len(x); i = 0
    while i < len(s):
        j = i
        while j + 1 < len(s) and x[s[j + 1]] == x[s[i]]:
            j += 1
        for k in range(i, j + 1):
            r[s[k]] = (i + j) / 2 + 1
        i = j + 1
    return r


def pearson(a, b):
    n = len(a); ma, mb = sum(a) / n, sum(b) / n
    sa = math.sqrt(sum((x - ma) ** 2 for x in a)); sb = math.sqrt(sum((x - mb) ** 2 for x in b))
    return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / (sa * sb) if sa and sb else None


cor = PROC / "tamano_lugar_correlaciones.csv"
with open(cor, "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh, lineterminator="\n")
    w.writerow(["clave", "familia", "localidades", "spearman_poblacion", "pearson_log_poblacion"])
    for c in claves:
        for f in familias:
            xs, ys, lp = [], [], []
            for k in locs:
                pos = sum(v.get((c, k[0], k[1], g), 0) for g in familias)
                if pos and v.get((c, k[0], k[1], f)):
                    xs.append(pob[k]); lp.append(math.log10(pob[k])); ys.append(100 * v[(c, k[0], k[1], f)] / pos)
            if len(xs) >= 5:
                w.writerow([c, f, len(xs), f"{pearson(rangos(xs), rangos(ys)):.3f}", f"{pearson(lp, ys):.3f}"])

# JSON compacto
J = {"cat": [e[1] for e in escala],
     "escala": [[e[1], e[2], e[3]] for e in escala],
     "fam": familias,
     "loc": [{"n": k[1], "d": k[0], "p": pob[k], "c": [e[1] for e in escala].index(categoria(pob[k]))} for k in locs],
     "el": claves, "v": {}}
for c in claves:
    J["v"][c] = []
    for i, k in enumerate(locs):
        J["v"][c].append([x for f_i, f in enumerate(familias) for x in (f_i, v.get((c, k[0], k[1], f), 0))
                          if v.get((c, k[0], k[1], f), 0)] if False else
                         [y for f_i, f in enumerate(familias) if v.get((c, k[0], k[1], f), 0)
                          for y in (f_i, v[(c, k[0], k[1], f)])])
(RAIZ / "salida" / "datos_tamano_lugar.json").write_text(
    json.dumps(J, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

# informe
print("Localidades por categoría:")
por_cat = collections.Counter(categoria(pob[k]) for k in locs)
for _, n, d, h in escala:
    print(f"  {n:18} {d:>6} a {h if h else '—':>6}: {por_cat.get(n, 0)} localidades",
          "(sin localidades en la base)" if not por_cat.get(n) else "")
print("Cerca de un límite (±3 %):", [(k[1], pob[k]) for k in locs
      if any(h and abs(pob[k] - h) / h <= 0.03 for _, _, _, h in escala)] or "ninguna")
print("Electores/población fuera de 0,5-0,95:", raros or "ninguna")
print("Elecciones con datos por localidad:", ", ".join(claves))
if error:
    print("\nERROR:"); [print(" ", e) for e in error]; sys.exit(1)
print("Controles: sin errores.")
