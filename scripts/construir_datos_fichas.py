#!/usr/bin/env python3
"""
Datos para las pestañas «Elecciones» y «Partidos» del tablero.

Resultados por **etiqueta tal como figura en cada elección**, sin agrupar en familias,
al nivel más fino disponible (circuito). Departamento y provincia se obtienen sumando
circuitos en el navegador.

Entradas
  --proc   carpeta con los datos procesados de la rama de datos:
           resultados_circuito_polar.csv, 2023_{PASO,GENERAL,BALOTAJE}_circuito.csv
  --cache  carpeta con los Excel de la DINE (se descargan si faltan), para el nombre
           oficial de cada etiqueta y el total provincial definitivo
  --html   tablero actual; se usa para validar contra los circuitos que ya contiene

Salida
  salida/datos_fichas.json

Recuento: provisorio (PolAr y DINE). El total provincial definitivo de la DINE se
incluye como referencia cuando existe.
"""
import argparse
import collections
import csv
import difflib
import json
import re
import unicodedata
import urllib.request
from pathlib import Path

import openpyxl

RAIZ = Path(__file__).resolve().parent.parent
WEB = "https://www.argentina.gob.ar/sites/default/files/"
ORDEN = {"PASO": 0, "GENERAL": 1, "BALOTAJE": 2}
NO_POSITIVOS = ("blancos", "nulos", "impugnados", "recurridos", "comando")
FUENTES_2023 = ["2023_PASO_circuito.csv", "2023_GENERAL_circuito.csv", "2023_BALOTAJE_circuito.csv"]

# Excel de la DINE con el distrito de Santa Fe: (anio, instancia) -> (archivo, hoja, formato)
EXCEL = {
    ("2003", "GENERAL"): ("resultados_2003_presidente_y_vicepresidente.xlsx", "Santa Fe", "A"),
    ("2007", "GENERAL"): ("resultados_2007_presidente_y_vicepresidente.xlsx", "Santa Fe", "A"),
    ("2011", "PASO"): ("resultados_2011_eleccion_paso_presidente_y_vicepresidente.xlsx", "Santa Fe", "A"),
    ("2011", "GENERAL"): ("resultados_2011_generales_presidente_y_vicepresidente.xlsx", "Santa Fe", "A"),
    ("2015", "PASO"): ("resultados_2015_elecciones_paso_presidente_y_vicepresidente.xlsx", "Santa Fe", "B"),
    ("2015", "GENERAL"): ("resultados_2015_nacionales_presidente_y_vicepresidente.xlsx", "Santa Fe", "B"),
    ("2015", "BALOTAJE"): ("resultados_2015_segunda_vuelta_presidente_y_vicepresidente.xlsx", "Santa Fe", "B"),
    ("2019", "GENERAL"): ("p.v._definitivo_x_distrito_grales_2019.xlsx", "SANTA FE", "B"),
}

# Vínculos entre etiquetas que cambiaron de nombre. Es una ayuda de navegación: no
# supone que se trate del mismo partido. Cada vínculo declara su fuente.
VINCULOS = [
    ("frente para la victoria", "frente de todos",
     "Continuidad habitual del peronismo kirchnerista; las fuentes leídas no la afirman con esas palabras."),
    ("frente de todos", "union por la patria",
     "Scaramella (2025), p. 104: Unión por la Patria es la misma coalición que ganó en 2019 como Frente de Todos."),
    ("cambiemos", "juntos por el cambio",
     "Murillo y Oliveros (2024), pp. 177-178: la coalición de 2015-2019 «fue rebautizada JXC»."),
    ("afirmacion para una republica igualitaria", "confederacion coalicion civica",
     "El nombre conserva «Afirmación» y la cabeza de lista es la misma (Elisa Carrió); la DINE incluye en 2007 al partido Afirmación para una República Igualitaria."),
    ("confederacion coalicion civica", "coalicion civica afirmacion para una republica igualitaria ari",
     "Misma cabeza de lista (Elisa Carrió) y el nombre vuelve a incluir «Afirmación para una República Igualitaria»."),
    ("frente de izquierda y de los trabajadores", "frente de izquierda y de trabajadores unidad",
     "El nombre cambia solo en una palabra («Trabajadores» a «Trabajadores - Unidad»)."),
]


def sin_tildes(s):
    return "".join(c for c in unicodedata.normalize("NFD", str(s)) if unicodedata.category(c) != "Mn")


def clave_etiqueta(s):
    """Clave estable de una etiqueta: sin tildes, sin «alianza» ni signos."""
    s = sin_tildes(s).lower()
    s = re.sub(r"\b(alianza|al\.?|confederacion\b(?= coalicion))\b", " ", s)
    s = re.sub(r"\(.*?\)", " ", s)
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


ACENTOS = {"union": "Unión", "accion": "Acción", "pais": "País", "democratico": "Democrático",
           "civica": "Cívica", "republica": "República", "coalicion": "Coalición", "integracion": "Integración",
           "politica": "Política", "izquierda": "Izquierda", "liber.ar": "Liber.Ar"}
SIGLAS = {"mst", "pro", "ari"}


def pct_titulo(s):
    """Nombre legible: pasa las etiquetas en mayúsculas a capitalización normal, con tildes y siglas."""
    s = s.strip()
    if s != s.upper():
        return s
    chicas = {"de", "del", "la", "las", "los", "y", "por", "para", "el", "en", "a", "al", "con", "una"}
    out = []
    for i, w in enumerate(s.lower().split()):
        nucleo = w.strip("()-")
        if nucleo in SIGLAS or (w.startswith("(") and w.endswith(")")):
            out.append(w.replace(nucleo, nucleo.upper()))
        elif nucleo in ACENTOS:
            out.append(w.replace(nucleo, ACENTOS[nucleo]))
        elif i and w in chicas:
            out.append(w)
        else:
            out.append(w.capitalize())
    return " ".join(out)


def cargar_dine(cache, anio, inst):
    """Etiquetas y votos definitivos de Santa Fe: ([(nombre, votos)], totales del distrito)."""
    archivo, hoja, fmt = EXCEL[(anio, inst)]
    destino = cache / archivo
    if not destino.exists():
        cache.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(WEB + archivo, destino)
    ws = openpyxl.load_workbook(destino, read_only=True, data_only=True)[hoja]
    out, tot = [], {}
    for r in ws.iter_rows(values_only=True):
        f = [c for c in r if c is not None]
        if not f:
            continue
        rot = str(f[0]).replace("\xa0", " ").strip().upper() if isinstance(f[0], str) else ""
        if rot.startswith("ELECTORES") and len(f) > 1:
            tot["electores"] = int(f[1])
        elif rot.startswith("VOTOS EN BLANCO") and len(f) > 1:
            tot["blancos"] = int(f[1])
        elif rot.startswith("VOTOS NULOS") or rot.startswith("VOTOS ANULADOS"):
            tot["nulos"] = int(f[1])
        elif rot.startswith("TOTAL DE VOTANTES") and len(f) > 1:
            tot["votantes"] = int(f[1])
        elif rot.startswith("VOTOS POSITIVOS"):
            tot["positivos"] = int(f[1])
        if fmt == "B":
            if isinstance(f[0], int) and len(f) >= 3 and isinstance(f[2], (int, float)):
                out.append((str(f[1]).strip(), int(f[2])))
        else:
            nums = [c for c in f if isinstance(c, (int, float))]
            txt = [c for c in f if isinstance(c, str)]
            if len(nums) == 2 and nums[0] >= nums[1] and len(txt) > 1 and "-" in txt[0]:
                out.append((txt[1].strip(), int(nums[0])))
    return out, tot


def emparejar(base, dine):
    """Asigna a cada etiqueta de la base su nombre oficial: parecido de texto y cercanía de votos."""
    pares = []
    for i, (nb, vb) in enumerate(base):
        for j, (nd, vd) in enumerate(dine):
            sim = difflib.SequenceMatcher(None, clave_etiqueta(nb), clave_etiqueta(nd)).ratio()
            cerca = 1 - min(1, abs(vb - vd) / max(vb, vd, 1))
            pares.append((sim * 0.6 + cerca * 0.4, i, j))
    usados_b, usados_d, res = set(), set(), {}
    for score, i, j in sorted(pares, reverse=True):
        if i in usados_b or j in usados_d or score < 0.62:
            continue
        usados_b.add(i)
        usados_d.add(j)
        res[i] = j
    return res


ARTICULOS = {"de", "del", "la", "las", "los", "y"}
ALIAS_DEP = {"9 DE JULIO": "Nueve de Julio", "NUEVE DE JULIO": "Nueve de Julio", "ROSARIO BARR.": "Rosario",
             "ROSARIO CAMP.": "Rosario", "LA CAPITAL CAMP.": "La Capital"}


def normalizar_depto(s):
    """Unifica mayúsculas y las subdivisiones de 2011 (misma regla que usa el tablero)."""
    s = (s or "").strip()
    alias = ALIAS_DEP.get(sin_tildes(s).upper())
    if alias:
        return alias
    return " ".join(p.capitalize() if i == 0 or p.lower() not in ARTICULOS else p.lower()
                    for i, p in enumerate(s.split()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--proc", default=str(RAIZ / "datos" / "procesados"))
    ap.add_argument("--cache", default=str(RAIZ / "datos" / "crudos" / "dine_nacional"))
    ap.add_argument("--html", default=str(RAIZ / "salida" / "voto_santafesino.html"))
    ap.add_argument("--csv2011", default=str(RAIZ / "datos" / "crudos" / "otras_fuentes" /
                                             "datos_electorales_presidente_santafe_2011_2023.csv"))
    ap.add_argument("--salida", default=str(RAIZ / "salida" / "datos_fichas.json"))
    a = ap.parse_args()
    proc, cache = Path(a.proc), Path(a.cache)

    html = Path(a.html).read_text(encoding="utf-8")
    i0 = html.index("const D = ")
    D = json.loads(html[i0 + len("const D = "):html.index("\n", i0)].rstrip(";"))
    deptos = D["departamentos"]
    i0 = html.index("const M = ")
    M = json.loads(html[i0 + len("const M = "):html.index("\n", i0)].rstrip(";"))

    votos = collections.defaultdict(lambda: collections.defaultdict(lambda: collections.defaultdict(int)))
    otros = collections.defaultdict(lambda: collections.defaultdict(lambda: collections.defaultdict(int)))
    electores = collections.defaultdict(dict)
    depto_de = collections.defaultdict(dict)
    nomen = {r["circuito_id"]: int(float(r["electores"] or 0))
             for r in csv.DictReader(open(proc / "nomenclador_circuitos_2023.csv", encoding="utf-8"))}
    fuentes = [proc / "resultados_circuito_polar.csv"] + [proc / f for f in FUENTES_2023]
    for ruta in fuentes:
        for r in csv.DictReader(open(ruta, encoding="utf-8")):
            k = (r["anio"], r["instancia"])
            c, t, n = r["circuito_id"], r["tipo_registro"], int(float(r["votos"]))
            dep = normalizar_depto(r["seccion"])
            depto_de[k][c] = deptos.index(dep)
            e = int(float(r.get("electores") or 0)) or (nomen.get(c, 0) if r["anio"] == "2023" else 0)
            if e:
                electores[k][c] = e
            if t == "agrupacion":
                votos[k][c][r["agrupacion"].strip()] += n
            elif t in NO_POSITIVOS:
                otros[k][c][t] += n

    extra_csv = collections.defaultdict(list)       # etiquetas del CSV recibido que la base no tiene
    mapa_inst = {"GENERALES": "GENERAL", "BALLOTAGE": "BALOTAJE", "PASO": "PASO"}
    if Path(a.csv2011).exists():
        por = collections.defaultdict(list)
        for r in csv.DictReader(open(a.csv2011, encoding="utf-8")):
            if r["Partido"] in ("BLANCO", "NULO", "IMPUGNADO"):
                continue
            t, an = r["Elecciones"].split()
            por[(an, mapa_inst[t])].append((r["Partido"], int(r["Votos"])))
        csv_por = por
    else:
        csv_por = {}

    elecciones = sorted(votos, key=lambda k: (k[0], ORDEN[k[1]]))
    salida = {"el": [f"{a}-{i}" for a, i in elecciones], "pt": {}, "ci": {}, "no": {}, "de": {}, "pa": {},
              "def": {}, "vi": []}
    informe = []
    for k in elecciones:
        clave = f"{k[0]}-{k[1]}"
        total = collections.Counter()
        for c, d in votos[k].items():
            total.update(d)
        base = sorted(total.items(), key=lambda x: -x[1])
        oficial, definitivo = {}, {}
        dine = []
        if k in EXCEL:
            dine, totales = cargar_dine(cache, *k)
            for i, j in emparejar(base, dine).items():
                oficial[i] = dine[j][0]
                definitivo[i] = dine[j][1]
            salida["def"][clave] = totales
        # etiquetas de la base que son parte de un nombre oficial más largo (se presentan juntas)
        usados = set(oficial.values())
        grupo = {}
        for j, (nd, vd) in enumerate(dine):
            if nd in usados:
                continue
            miembros = [i for i, (nb, vb) in enumerate(base)
                        if i not in oficial and sin_tildes(nb).lower() in sin_tildes(nd).lower()]
            if len(miembros) > 1:
                for i in miembros:
                    grupo[i] = j
                informe.append(f"  se unen en {clave}: {[base[i][0] for i in miembros]} -> {nd}")
        # índice de partido por etiqueta de la base
        idx, pt, nuevo_i = {}, [], {}
        for i, (etq, v) in enumerate(base):
            if i in grupo:
                j = grupo[i]
                if j not in nuevo_i:
                    nuevo_i[j] = len(pt)
                    pt.append({"k": clave_etiqueta(dine[j][0]), "n": pct_titulo(dine[j][0]), "o": [], "v": 0,
                               "d": dine[j][1]})
                idx[etq] = nuevo_i[j]
                pt[nuevo_i[j]]["o"].append(etq)
                pt[nuevo_i[j]]["v"] += v
                continue
            nom = oficial.get(i, etq)
            idx[etq] = len(pt)
            pt.append({"k": clave_etiqueta(nom), "n": pct_titulo(nom), "o": [etq], "v": v,
                       "d": definitivo.get(i)})
            if k in EXCEL and i not in oficial:
                informe.append(f"  sin nombre oficial: {clave} · {etq} ({v})")
        # etiquetas del CSV recibido que no existen en la base (solo total provincial)
        if k in csv_por:
            nombres_base = [(p["n"], p["v"]) for p in pt]
            emp = emparejar(nombres_base, csv_por[k])
            for j, (nc, vc) in enumerate(csv_por[k]):
                if j not in emp.values():
                    pt.append({"k": clave_etiqueta(nc), "n": pct_titulo(nc), "o": [nc], "v": vc, "d": None,
                               "sd": 1})
                    informe.append(f"  solo en el CSV recibido: {clave} · {nc} ({vc})")
        # orden por votos
        orden = sorted(range(len(pt)), key=lambda i: -pt[i]["v"])
        remap = {old: new for new, old in enumerate(orden)}
        salida["pt"][clave] = [pt[i] for i in orden]
        salida["ci"][clave] = {}
        for c, d in votos[k].items():
            suma = collections.Counter()
            for e, n in d.items():
                suma[remap[idx[e]]] += n
            salida["ci"][clave][c] = [x for pi, n in suma.most_common() for x in (pi, n)]
        salida["no"][clave] = {c: [d.get(t, 0) for t in NO_POSITIVOS] for c, d in otros[k].items()}
        salida["de"][clave] = depto_de[k]
        salida["pa"][clave] = electores[k]
    claves = {p["k"] for pts in salida["pt"].values() for p in pts}
    salida["vi"] = [[x, y, f] for x, y, f in VINCULOS if x in claves and y in claves]
    salida["no_cols"] = list(NO_POSITIVOS)
    salida["dep"] = deptos

    # validación contra los circuitos que ya usa el tablero
    malos, sin_geo = 0, 0
    for clave, circ in salida["ci"].items():
        ref = M["cir"][clave]
        sin_geo += len(set(circ) - set(ref))
        if set(ref) - set(circ):
            informe.append(f"  circuitos del tablero ausentes en {clave}: {len(set(ref) - set(circ))}")
        for c, plano in circ.items():
            if c in ref and sum(plano[1::2]) != sum(ref[c][1::2]):
                malos += 1
    informe.append(f"  circuitos comunes con total distinto del tablero: {malos}; circuitos sin polígono: {sin_geo}")

    texto = json.dumps(salida, ensure_ascii=False, separators=(",", ":"))
    Path(a.salida).write_text(texto, encoding="utf-8")
    print(f"{len(elecciones)} elecciones · {sum(len(v) for v in salida['pt'].values())} filas de partido · "
          f"{len(texto)/1024:.0f} KB · {len(salida['vi'])} vínculos")
    print("\n".join(informe))


if __name__ == "__main__":
    main()
