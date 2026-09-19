#!/usr/bin/env python3
"""
Aplica la tabla de homologación para que los años sean comparables.

El problema tiene dos capas y esta tabla resuelve las dos por separado:

1. VARIACION DE ESCRITURA (mecánica). La misma fuerza aparece escrita distinto
   según la fuente: "ALIANZA FRENTE PARA LA VICTORIA" y "Alianza Frente para
   la Victoria" son la misma, igual que "ALIANZA CAMBIEMOS" y "CAMBIEMOS".
   La columna `agrupacion_homologada` unifica la escritura.

2. CONTINUIDAD POLITICA (interpretativa). Decidir que el Frente para la
   Victoria, el Frente de Todos y Unión por la Patria son la misma corriente
   es una decisión de investigación, no un hecho del dato. Las columnas
   `familia` y `bloque` la explicitan, y cambiarlas es editar el CSV: el
   código no fija ningún criterio.

`bloque` implementa el eje kirchnerismo / no kirchnerismo que el plan de
investigación toma como estructurante desde el conflicto agrario de 2008.

Salida: datos/procesados/serie_homologada.csv
"""
import csv
import sys
from collections import defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PROC = RAIZ / "datos" / "procesados"
TABLA = RAIZ / "datos" / "referencia" / "homologacion_agrupaciones.csv"

# El nivel más fino disponible de cada elección, sin superponer fuentes.
FUENTES = [
    ("2023_PASO_circuito.csv", "circuito"),
    ("serie_localidad.csv", "localidad"),
    ("resultados_departamento.csv", "departamento"),
    ("resultados_provincia_transcripto.csv", "provincia"),
    ("resultados_provincia_dine.csv", "provincia"),
    ("resultados.csv", "provincia"),
]

COLUMNAS = ["anio", "instancia", "nivel", "universo", "seccion_id", "seccion",
            "localidad",
            "circuito_id", "agrupacion_original", "agrupacion_homologada",
            "familia", "bloque", "votos"]

# Homologar las etiquetas no alcanza: una serie solo es comparable si además
# las unidades geograficas son las mismas todos los anios. `universo` marca
# a que recorte pertenece cada fila, y NUNCA deben mezclarse dos universos en
# una misma serie temporal.
UNIVERSOS = {"localidad": "zona_nucleo_30_localidades",
             "circuito": "provincia_completa",
             "departamento": "provincia_completa",
             "provincia": "provincia_completa"}


def cargar_tabla():
    if not TABLA.exists():
        sys.exit(f"falta {TABLA}")
    return {(r["anio"], r["instancia"], r["agrupacion_original"].strip()): r
            for r in csv.DictReader(open(TABLA, encoding="utf-8"))}


def main():
    tabla = cargar_tabla()
    filas, sin_mapear = [], set()
    # Una eleccion puede existir en dos niveles a la vez (2023 PASO esta por
    # circuito y por localidad). Se conservan ambos, diferenciados por
    # `universo`, porque cada uno sirve para una serie distinta. Al sumar hay
    # que filtrar por universo o se cuenta dos veces.

    for nombre, nivel in FUENTES:
        ruta = PROC / nombre
        if not ruta.exists():
            continue
        for r in csv.DictReader(open(ruta, encoding="utf-8")):
            if r["tipo_registro"] != "agrupacion":
                continue
            clave = (r["anio"], r["instancia"])

            etiqueta = r["agrupacion"].strip()
            h = tabla.get((*clave, etiqueta))
            if not h:
                sin_mapear.add((*clave, etiqueta))
                continue
            filas.append({
                "anio": r["anio"], "instancia": r["instancia"], "nivel": nivel,
                "universo": UNIVERSOS[nivel],
                "seccion": r.get("seccion", ""),
                "localidad": r.get("localidad", ""),
                "circuito_id": r.get("circuito_id", ""),
                "seccion_id": r.get("seccion_id", ""),
                "agrupacion_original": etiqueta,
                "agrupacion_homologada": h["agrupacion_homologada"],
                "familia": h["familia"], "bloque": h["bloque"],
                "votos": int(float(r["votos"])),
            })

    destino = PROC / "serie_homologada.csv"
    with open(destino, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNAS)
        w.writeheader()
        w.writerows(filas)
    print(f"-> datos/procesados/{destino.name} ({len(filas)} filas)")

    if sin_mapear:
        print(f"\n! {len(sin_mapear)} etiquetas sin homologar "
              f"(agregarlas a la tabla):")
        for s in sorted(sin_mapear):
            print("   ", s)
        sys.exit(1)
    print("\nCobertura: todas las etiquetas tienen homologación.\n")

    # Se informa que series son comparables, para no inducir a compararlas mal.
    por_universo = defaultdict(set)
    for f in filas:
        por_universo[f["universo"]].add((f["anio"], f["instancia"]))
    orden = {"PASO": 0, "GENERAL": 1, "BALOTAJE": 2}
    for universo, elecciones in sorted(por_universo.items()):
        print(f"universo '{universo}': {len(elecciones)} instancias")
        for anio, inst in sorted(elecciones, key=lambda e: (e[0], orden[e[1]])):
            print(f"   {anio} {inst}")
    print("\nNo comparar entre universos distintos: son recortes "
          "geograficos diferentes.")


if __name__ == "__main__":
    main()
