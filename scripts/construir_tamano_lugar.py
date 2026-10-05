#!/usr/bin/env python3
"""
El voto según el tamaño del lugar: toda la provincia, 12 instancias, por localidad censal.

Cadena de datos
  circuito (resultados) ──► localidad / gobierno local (cartografía × radios del Censo 2022)
                         ──► población 2022 ──► categoría de la escala demográfica ──► voto por familia

Entradas
  datos/procesados/serie_homologada.csv          resultados por circuito (nivel `circuito`) con familia política
  datos/referencia/circuito_localidad.csv        circuito → localidad (scripts/asignar_circuitos_a_localidad.py)
  datos/referencia/escala_tamano_lugar.csv       escala demográfica (Rural … Ciudad grande)
  datos/procesados/nomenclador_circuito_localidad.csv   30 localidades relevadas a mano (control)
  datos/procesados/serie_homologada.csv (nivel `localidad`)  resultados por localidad de esas 30 (control)

Salidas
  datos/procesados/tamano_lugar.csv               localidad × elección × familia, con población y categoría
  datos/procesados/tamano_lugar_correlaciones.csv correlación población-voto por elección y familia
  salida/datos_tamano_lugar.json                  versión compacta para el tablero

Controles (los de tipo ERROR detienen el proceso)
  1. cada circuito con votos tiene localidad asignada y se informa qué porción de los votos queda sin asignar;
  2. el cruce espacial reproduce el nomenclador circuito→localidad relevado a mano;
  3. para las 30 localidades con resultados propios, los votos reconstruidos desde los circuitos se comparan
     con los de la fuente por localidad, elección por elección;
  4. cuántas localidades y qué porción del voto cae en cada categoría.
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
CAPA = lambda a: "2003" if a <= 2003 else "2007" if a <= 2007 else "2011" if a <= 2011 else "2015" if a <= 2015 else "2019" if a <= 2019 else "2023"
nz = lambda c: c.lstrip("0")


def leer(p):
    return list(csv.DictReader(open(p, encoding="utf-8")))


escala = [(int(r["orden"]), r["categoria"], int(r["desde"]), int(r["hasta"]) if r["hasta"] else None)
          for r in leer(REF / "escala_tamano_lugar.csv")]
nombres_cat = [e[1] for e in escala]


def categoria(p):
    for _, nombre, d, h in escala:
        if p >= d and (h is None or p <= h):
            return nombre
    raise ValueError(p)


asig = {(r["capa"], nz(r["circuito"])): r for r in leer(REF / "circuito_localidad.csv")}
serie = leer(PROC / "serie_homologada.csv")
error = []

# votos por (elección, localidad, familia) reconstruidos desde los circuitos
v = collections.defaultdict(int)
sin_asignar = collections.defaultdict(int)
total_elec = collections.defaultdict(int)
circ_por_loc = collections.defaultdict(set)
for r in serie:
    if r["nivel"] != "circuito":
        continue
    c = f"{r['anio']}-{r['instancia']}"
    x = int(float(r["votos"]))
    total_elec[c] += x
    a = asig.get((CAPA(int(r["anio"])), nz(r["circuito_id"])))
    if not a:
        sin_asignar[c] += x
        continue
    v[(c, a["codigo_gobierno_local"], r["familia"])] += x
    if r["anio"] == "2023":
        circ_por_loc[a["codigo_gobierno_local"]].add(nz(r["circuito_id"]))
claves = sorted(total_elec, key=lambda c: (c[:4], ORDEN[c[5:]]))
familias = sorted({k[2] for k in v})
loc_info = {}
for a in asig.values():
    loc_info[a["codigo_gobierno_local"]] = (a["localidad"], int(a["poblacion_localidad_2022"]))
con_votos = sorted({k[1] for k in v}, key=lambda g: (-loc_info[g][1], loc_info[g][0]))

# 1. cobertura
for c in claves:
    if total_elec[c] and sin_asignar[c] / total_elec[c] > 0.005:
        error.append(f"{c}: {100 * sin_asignar[c] / total_elec[c]:.2f} % de los votos sin localidad")

# 2. el cruce espacial contra el nomenclador a mano
nom_mal = []
for r in leer(PROC / "nomenclador_circuito_localidad.csv"):
    got = asig.get((r["anio"], nz(r["circuito_id"])))
    if not got or got["localidad"] != r["localidad"]:
        nom_mal.append((r["anio"], r["circuito_id"], r["localidad"], got["localidad"] if got else None))
n_nom = len(leer(PROC / "nomenclador_circuito_localidad.csv"))
if len(nom_mal) / n_nom > 0.05:
    error.append(f"el cruce espacial no reproduce el nomenclador: {nom_mal}")

# 3. las 30 localidades con resultados propios
nombre_a_gl = {loc_info[g][0]: g for g in loc_info}
dif = []
fuente = collections.defaultdict(int)
for r in serie:
    if r["nivel"] == "localidad":
        fuente[(f"{r['anio']}-{r['instancia']}", r["localidad"])] += int(float(r["votos"]))
for (c, loc), x in sorted(fuente.items()):
    g = nombre_a_gl.get(loc)
    rec = sum(w for (cc, gg, f), w in v.items() if cc == c and gg == g)
    dif.append((c, loc, x, rec, (rec - x) / x * 100 if x else 0))
fuera = [d for d in dif if abs(d[4]) > 10]

# salida larga
out = PROC / "tamano_lugar.csv"
with open(out, "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh, lineterminator="\n")
    w.writerow(["clave", "codigo_gobierno_local", "localidad", "poblacion_2022", "categoria", "familia", "votos"])
    for (c, g, f), x in sorted(v.items(), key=lambda t: (t[0][0], t[0][1], t[0][2])):
        w.writerow([c, g, loc_info[g][0], loc_info[g][1], categoria(loc_info[g][1]), f, x])


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


pos_loc = collections.defaultdict(int)
for (c, g, f), x in v.items():
    pos_loc[(c, g)] += x
with open(PROC / "tamano_lugar_correlaciones.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh, lineterminator="\n")
    w.writerow(["clave", "familia", "localidades", "spearman_poblacion", "pearson_log_poblacion"])
    for c in claves:
        for f in familias:
            xs, ys, lp = [], [], []
            for g in con_votos:
                p = pos_loc.get((c, g), 0)
                if p and v.get((c, g, f)):
                    xs.append(loc_info[g][1]); lp.append(math.log10(loc_info[g][1])); ys.append(100 * v[(c, g, f)] / p)
            if len(xs) >= 10:
                w.writerow([c, f, len(xs), f"{pearson(rangos(xs), rangos(ys)):.3f}", f"{pearson(lp, ys):.3f}"])

# JSON compacto
idx = {g: i for i, g in enumerate(con_votos)}
J = {"cat": nombres_cat, "escala": [[e[1], e[2], e[3]] for e in escala], "fam": familias,
     "loc": [{"n": loc_info[g][0], "p": loc_info[g][1], "c": nombres_cat.index(categoria(loc_info[g][1])),
              "k": len(circ_por_loc[g])} for g in con_votos],
     "el": claves, "v": {}}
for c in claves:
    J["v"][c] = {}
    for g in con_votos:
        plano = [y for fi, f in enumerate(familias) if v.get((c, g, f)) for y in (fi, v[(c, g, f)])]
        if plano:
            J["v"][c][idx[g]] = plano
(RAIZ / "salida" / "datos_tamano_lugar.json").write_text(
    json.dumps(J, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

# informe
print("Localidades con votos y votos de 2023 (general) por categoría:")
por_cat = collections.Counter(categoria(loc_info[g][1]) for g in con_votos)
vot23 = collections.defaultdict(int)
for g in con_votos:
    vot23[categoria(loc_info[g][1])] += pos_loc.get(("2023-GENERAL", g), 0)
t23 = sum(vot23.values())
for _, n, d, h in escala:
    print(f"  {n:18} {d:>6} a {h if h else '—':>6}: {por_cat.get(n, 0):>3} localidades · {100 * vot23[n] / t23:5.1f} % de los votos positivos 2023")
print("Votos sin localidad asignada (máx. por elección):",
      f"{max(100 * sin_asignar[c] / total_elec[c] for c in claves):.2f} %")
print(f"Nomenclador a mano reproducido: {n_nom - len(nom_mal)} de {n_nom}", nom_mal or "")
print("Control contra las 30 localidades con resultados propios:",
      f"{len(dif)} pares localidad-elección; diferencia media absoluta {sum(abs(d[4]) for d in dif) / len(dif):.1f} %;",
      f"mayor diferencia {max(abs(d[4]) for d in dif):.1f} %")
if fuera:
    print("  más de 10 % de diferencia:", sorted({(d[1], round(d[4])) for d in fuera})[:12])
cerca = [(loc_info[g][0], loc_info[g][1]) for g in con_votos
         if any(h and abs(loc_info[g][1] - h) / h <= 0.01 for _, _, _, h in escala)]
print("A ±1 % de un límite de categoría:", cerca or "ninguna")
if error:
    print("\nERROR:"); [print(" ", e) for e in error]; sys.exit(1)
print("Controles: sin errores.")
