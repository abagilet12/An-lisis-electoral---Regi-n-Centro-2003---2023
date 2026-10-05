#!/usr/bin/env python3
"""
Swing voters: cambio de ganador por circuito entre elecciones definitivas consecutivas.

Definición operativa (docs/SWING_VOTERS.md): un circuito «cambió» entre dos elecciones cuando la fuerza más
votada (familia política) es distinta de la que ganó el circuito en la elección anterior. Con datos agregados no
se observa a los votantes individuales: la señal es territorial.

Elecciones definitivas (las que definieron presidente): 2003, 2007, 2011 y 2019 generales; 2015 y 2023 balotaje.
Comparaciones: 2003-2007, 2007-2011, 2011-2015, 2015-2019 y 2019-2023.

Para cada par (a, b) las unidades son los circuitos de la elección b con polígono en la cartografía. Cada uno
se enlaza con el circuito que cubría ese territorio en a mediante el enlace histórico
(datos/referencia/enlace_circuitos.csv). Dirección de la flecha: según el movimiento en la escala
izquierda-derecha de datos/referencia/ubicacion_familias.csv, que ordena a las familias por su orientación
igualitaria (criterio de Bobbio, 1994; docs/CRITERIO_IDEOLOGICO_BOBBIO.md). Derecha si la nueva fuerza es menos
igualitaria que la que ganó antes.

Entradas  datos/procesados/serie_homologada.csv, datos/referencia/{enlace_circuitos, ubicacion_familias,
          circuito_localidad, escala_tamano_lugar, departamentos_codigos_cartografia}.csv, datos/geo/circuitos/
Salidas   datos/procesados/swing_circuitos.csv, datos/procesados/swing_resumen.csv, salida/datos_swing.json
"""
import collections
import csv
import json
import sys
from pathlib import Path

from shapely.geometry import shape

RAIZ = Path(__file__).resolve().parent.parent
PROC, REF, GEO = RAIZ / "datos" / "procesados", RAIZ / "datos" / "referencia", RAIZ / "datos" / "geo" / "circuitos"
DEF = ["2003-GENERAL", "2007-GENERAL", "2011-GENERAL", "2015-BALOTAJE", "2019-GENERAL", "2023-BALOTAJE"]
CAPA = lambda a: "2003" if a <= 2003 else "2007" if a <= 2007 else "2011" if a <= 2011 else "2015" if a <= 2015 else "2019" if a <= 2019 else "2023"
nz = lambda c: c.lstrip("0")
Q = 10000


def leer(p):
    return list(csv.DictReader(open(p, encoding="utf-8")))


# escala izquierda-derecha
_ub = leer(REF / "ubicacion_familias.csv")
if len({r["igualitarismo"] for r in _ub}) != len(_ub):
    sys.exit("dos familias comparten el mismo puntaje de igualitarismo: el orden debe ser estricto")
# puntaje = igualitarismo (Bobbio): menor = más igualitario = más a la izquierda
esc = {r["familia"]: (float(r["igualitarismo"]), int(r["posicion"]), r["posicion_nombre"]) for r in sorted(_ub, key=lambda r: float(r["igualitarismo"]))}
puntaje = lambda f: esc[f][0] if f in esc else None
misma_pos = lambda a, b: a in esc and b in esc and esc[a][1] == esc[b][1]

# votos por circuito
votos = collections.defaultdict(lambda: collections.defaultdict(lambda: collections.defaultdict(int)))
for r in leer(PROC / "serie_homologada.csv"):
    if r["nivel"] == "circuito":
        votos[f"{r['anio']}-{r['instancia']}"][nz(r["circuito_id"])][r["familia"]] += int(float(r["votos"]))
familias = sorted({f for c in DEF for d in votos[c].values() for f in d})
fid = {f: i for i, f in enumerate(familias)}

# enlace histórico
enlace = leer(REF / "enlace_circuitos.csv")
def mapa_enlace(ya, yb):
    m = collections.defaultdict(collections.Counter)
    for r in enlace:
        m[nz(r[f"circuito_{yb}"])][nz(r[f"circuito_{ya}"])] += 1
    return {b: c.most_common(1)[0][0] for b, c in m.items()}

# localidad y categoría
cats = [r["categoria"] for r in leer(REF / "escala_tamano_lugar.csv")]
loc = {(r["capa"], nz(r["circuito"])): (r["localidad"], r["poblacion_localidad_2022"]) for r in leer(REF / "circuito_localidad.csv")}
pobl = {}
for r in leer(PROC / "tamano_lugar.csv"):
    pobl[r["localidad"]] = r["categoria"]
deptos = {(r["corte"][:4], r["coddepto"]): r["departamento"] for r in leer(REF / "departamentos_codigos_cartografia.csv")}
nomdep = sorted(set(deptos.values()))
nomloc = sorted({v[0] for v in loc.values()})

def ganador(d):
    """Fuerza más votada. Un empate exacto (ocurre en circuitos muy chicos) lo gana la primera en orden alfabético,
    con La Libertad Avanza al final: es el mismo criterio con el que el tablero colorea el mapa."""
    tot = sum(d.values())
    f = min(d, key=lambda k: (-d[k], k == "La Libertad Avanza", k))
    return f, d[f], tot

pares, filas, resumen, J = list(zip(DEF, DEF[1:])), [], [], {"fam": familias, "cat": cats, "dep": nomdep, "loc": nomloc,
    "esc": [[f, esc[f][1], i + 1, esc[f][2], esc[f][0]] for i, f in enumerate(esc)], "pares": []}
for a, b in pares:
    ya, yb = a[:4], b[:4]
    capa_b = CAPA(int(yb))
    eq = mapa_enlace(ya, yb)
    gj = json.load(open(GEO / f"santafe_circuitos_{capa_b}_reconstruido.geojson", encoding="utf-8"))
    corte = "2025" if capa_b == "2023" else "2021"
    unidades, cont, mp = [], collections.Counter(), 0
    sin_votos = 0
    for ft in gj["features"]:
        cb = nz(ft["properties"]["circuito"])
        db = votos[b].get(cb)
        if not db:
            sin_votos += 1; continue
        pt = shape(ft["geometry"]).representative_point()
        lc = loc.get((capa_b, cb))
        li = nomloc.index(lc[0]) if lc else -1
        ct = cats.index(pobl[lc[0]]) if lc and lc[0] in pobl else -1
        de = deptos.get((corte, ft["properties"]["coddepto"]))
        di = nomdep.index(de) if de else -1
        wb, vb, tb = ganador(db)
        ca = eq.get(cb); da = votos[a].get(ca) if ca else None
        if da:
            wa, va, ta = ganador(da)
            if wa != wb and misma_pos(wa, wb):
                mp += 1
            if wa == wb:
                d = 0
            elif puntaje(wa) is None or puntaje(wb) is None:
                d = 8
            else:
                d = 1 if puntaje(wb) > puntaje(wa) else -1
            ob = da and db.get(wa, 0)
            fila = [cb, ca, fid[wa], fid[wb], round(1000 * va / ta), round(1000 * vb / tb), round(1000 * ob / tb), d]
        else:
            d, fila = 9, [cb, "", -1, fid[wb], 0, round(1000 * vb / tb), 0, 9]
        cont[(d, ct)] += 1
        unidades.append(fila + [round(pt.x * Q), round(pt.y * Q), li, di, ct])
        filas.append([a, b, cb, ca or "", wa if da else "", wb, d, round(vb / tb * 100, 1)])
    J["pares"].append({"a": a, "b": b, "u": unidades})
    tot = sum(cont.values())
    n = collections.Counter()
    for (d, ct), c in cont.items():
        n[d] += c
    resumen.append([a, b, tot, n[0], n[1], n[-1], n[8], n[9], mp])
    print(f"{a} → {b}: {tot} circuitos · continuidad {n[0]} · a la derecha {n[1]} · a la izquierda {n[-1]} · "
          f"sin ubicación {n[8]} · sin enlace {n[9]} · cambios dentro de la misma posición {mp}")

with open(PROC / "swing_circuitos.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh, lineterminator="\n")
    w.writerow(["eleccion_a", "eleccion_b", "circuito_b", "circuito_a", "ganador_a", "ganador_b", "direccion", "pct_ganador_b"])
    w.writerows(filas)
with open(PROC / "swing_resumen.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh, lineterminator="\n")
    w.writerow(["eleccion_a", "eleccion_b", "circuitos", "continuidad", "cambio_a_la_derecha", "cambio_a_la_izquierda", "sin_ubicacion", "sin_enlace", "cambios_dentro_de_la_misma_posicion"])
    w.writerows(resumen)
(RAIZ / "salida" / "datos_swing.json").write_text(json.dumps(J, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print("JSON:", round((RAIZ / "salida" / "datos_swing.json").stat().st_size / 1024), "KB")
