#!/usr/bin/env python3
"""
Construye la capa de circuitos que corresponde a cada eleccion.

La cartografia disponible tiene dos cortes, 2021 y 2025, y ninguno coincide
exactamente con los circuitos de todas las elecciones:

- **2003-2019** usan el corte 2021, con codigos de 4 digitos contra los 5 de
  la capa. Es solo relleno de ceros: normalizando cruzan el 99,8 % de los
  votos.
- **2023** usa el corte 2025, pero entre 2023 y 2025 la provincia
  **subdividio** circuitos: 20 codigos de 2023 ya no existen como tales en la
  capa, y entre ellos esta buena parte de Rosario, el 22,8 % de los votos.

La subdivision sigue una regla regular: el circuito `0XYZ0` se partio en
`0XYZ1`...`0XYZ9`. Asi que el poligono de 2023 se reconstruye **uniendo los
hijos**, sin trabajo manual y sin perder superficie.

Salida: datos/geo/circuitos/santafe_circuitos_<anio>_reconstruido.geojson
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

from shapely.geometry import mapping, shape
from shapely.ops import unary_union

RAIZ = Path(__file__).resolve().parent.parent
GEO = RAIZ / "datos" / "geo" / "circuitos"

CORTES = {"2021": GEO / "santafe_circuitos_2021.geojson",
          "2025": GEO / "santafe_circuitos_2025.geojson"}
# Que corte usar para cada anio de eleccion.
CORTE_DE = {"2003": "2021", "2007": "2021", "2011": "2021",
            "2015": "2021", "2019": "2021", "2023": "2025"}


def normalizar(codigo):
    """Los codigos vienen con distinto relleno segun la fuente."""
    return str(codigo).strip().lstrip("0") or "0"


def cargar(corte):
    d = json.loads(CORTES[corte].read_text(encoding="utf-8"))
    capa = {}
    for f in d["features"]:
        g = f.get("geometry")
        if not g or not g.get("coordinates"):
            continue          # sub-circuitos con letra, sin geometria
        capa[f["properties"]["circuito"]] = (shape(g), f["properties"])
    return capa


def construir(anio, circuitos_datos):
    """Devuelve {circuito_dato: (geometria, propiedades, origen)}."""
    capa = cargar(CORTE_DE[anio])
    por_norma = {normalizar(c): c for c in capa}

    # Indice de posibles hijos: los cuatro primeros caracteres del codigo.
    hijos = defaultdict(list)
    for c in capa:
        hijos[c[:4]].append(c)

    salida, sin_resolver = {}, []
    for cd in circuitos_datos:
        directo = por_norma.get(normalizar(cd))
        if directo:
            geom, props = capa[directo]
            # La capa se indexa por el codigo del DATO, no por el de la
            # cartografia: difieren en el relleno de ceros (0001 vs 00001) y
            # el cruce posterior se hace contra los resultados.
            props = {**props, "circuito": cd, "circuito_cartografia": directo}
            salida[cd] = (geom, props, "directo")
            continue

        # Subdivision posterior: se unen los hijos del mismo prefijo.
        candidatos = [c for c in hijos.get(cd[:4], []) if c != cd]
        if candidatos:
            geom = unary_union([capa[c][0] for c in candidatos])
            props = dict(capa[candidatos[0]][1])
            props["circuito"] = cd
            salida[cd] = (geom, props, f"union de {len(candidatos)}")
            continue
        sin_resolver.append(cd)
    return salida, sin_resolver


def main():
    if len(sys.argv) < 2:
        sys.exit("uso: construir_capa_circuitos.py <anio> [...]")

    import csv
    for anio in sys.argv[1:]:
        # Los circuitos que realmente aparecen en los datos de ese anio.
        # Solo los archivos de resultados: los nomencladores traen codigos
        # del padron, que son otro esquema y contaminarian el conjunto.
        fuentes = [RAIZ / "datos" / "procesados" / "resultados_circuito_polar.csv"]
        fuentes += sorted((RAIZ / "datos" / "procesados").glob("*_circuito.csv"))
        circuitos = set()
        for ruta in fuentes:
            if not ruta.exists():
                continue
            for r in csv.DictReader(open(ruta, encoding="utf-8")):
                if r.get("anio") == anio and r.get("circuito_id"):
                    circuitos.add(r["circuito_id"])
        if not circuitos:
            print(f"{anio}: sin datos de circuito")
            continue

        capa, faltan = construir(anio, sorted(circuitos))
        uniones = sum(1 for v in capa.values() if v[2].startswith("union"))
        destino = GEO / f"santafe_circuitos_{anio}_reconstruido.geojson"
        destino.write_text(json.dumps({
            "type": "FeatureCollection",
            "features": [{"type": "Feature", "properties": {**p, "origen": o},
                          "geometry": mapping(g)}
                         for g, p, o in capa.values()],
        }, ensure_ascii=False), encoding="utf-8")

        print(f"{anio}: {len(capa)} de {len(circuitos)} circuitos "
              f"({uniones} reconstruidos por unión) -> {destino.name}")
        if faltan:
            print(f"   sin resolver: {faltan}")


if __name__ == "__main__":
    main()
