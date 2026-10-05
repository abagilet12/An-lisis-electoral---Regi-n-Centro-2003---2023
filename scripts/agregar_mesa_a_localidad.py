#!/usr/bin/env python3
"""
Agrega el CSV por mesa de la DINE a nivel localidad, usando el nomenclador
circuito -> localidad del anio correspondiente.

El CSV por mesa es la unica fuente que llega por debajo del departamento. Se
agrupan las mesas por circuito y los circuitos por localidad, y se emite el
mismo esquema que scripts/parse_votos_localidad.py, de modo que la salida se
concatena con el resto de la serie.

ATENCION: estos archivos son del RECUENTO PROVISORIO, no del escrutinio
definitivo. La columna recuento_tipo lo declara y se copia a la salida para
que la diferencia quede a la vista y no se mezcle sin querer.

Uso:
    python3 scripts/agregar_mesa_a_localidad.py <csv> <anio> <instancia>
"""
import csv
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SALIDA = RAIZ / "datos" / "procesados"
NOMENCLADOR = SALIDA / "nomenclador_circuito_localidad.csv"

CARGO_PRESIDENTE = "1"
CARGO = "PRESIDENTE Y VICE"
DISTRITO_ID, DISTRITO = "21", "Santa Fe"

FECHAS = {("2023", "PASO"): "2023-08-13", ("2023", "GENERAL"): "2023-10-22",
          ("2023", "BALOTAJE"): "2023-11-19"}

# votos_tipo del origen -> tipo_registro de salida.
TIPOS_VOTO = {"EN BLANCO": "blancos", "NULO": "nulos",
              "IMPUGNADO": "impugnados", "RECURRIDO": "recurridos",
              "COMANDO": "comando"}

COLUMNAS = ["anio", "instancia", "fecha", "cargo", "distrito_id", "distrito",
            "seccion", "localidad", "circuito_id", "agrupacion",
            "tipo_registro", "votos", "recuento_tipo", "archivo_origen"]
COLUMNAS_META = ["anio", "instancia", "fecha", "distrito", "seccion",
                 "localidad", "mesas", "electores", "recuento_tipo",
                 "archivo_origen"]


def clave_circuito(c):
    """Los codigos vienen con distinto relleno segun el archivo."""
    return str(c).strip().lstrip("0")


def cargar_nomenclador(anio):
    loc = {}
    for r in csv.DictReader(open(NOMENCLADOR, encoding="utf-8")):
        if r["anio"] == anio:
            loc[clave_circuito(r["circuito_id"])] = (r["seccion"], r["localidad"])
    if not loc:
        sys.exit(f"el nomenclador no tiene entradas para {anio}")
    return loc


def agregar(ruta, anio, instancia):
    localidad_de = cargar_nomenclador(anio)
    votos, mesas, electores, sin_mapear = {}, {}, {}, set()

    with open(ruta, encoding="utf-8") as fh:
        for fila in csv.DictReader(fh):
            if fila["cargo_id"] != CARGO_PRESIDENTE:
                continue
            circuito = clave_circuito(fila["circuito_id"])
            destino = localidad_de.get(circuito)
            if destino is None:
                sin_mapear.add(circuito)
                continue

            cantidad = int(fila["votos_cantidad"] or 0)
            tipo = fila["votos_tipo"]
            etiqueta = (fila["agrupacion_nombre"] if tipo == "POSITIVO"
                        else tipo)
            registro = ("agrupacion" if tipo == "POSITIVO"
                        else TIPOS_VOTO.get(tipo, tipo.lower()))
            clave = (*destino, circuito, etiqueta, registro)
            votos[clave] = votos.get(clave, 0) + cantidad

            # El padron de la mesa se cuenta una sola vez, no por cada fila.
            mesa = (*destino, fila["mesa_id"])
            if mesa not in mesas:
                mesas[mesa] = True
                electores[destino] = (electores.get(destino, 0)
                                      + int(fila["mesa_electores"] or 0))

    comun = {"anio": anio, "instancia": instancia,
             "fecha": FECHAS.get((anio, instancia), ""), "cargo": CARGO,
             "distrito_id": DISTRITO_ID, "distrito": DISTRITO,
             "recuento_tipo": "PROVISORIO", "archivo_origen": Path(ruta).name}

    resultados = [
        {**comun, "seccion": s, "localidad": l, "circuito_id": c,
         "agrupacion": a, "tipo_registro": t, "votos": v}
        for (s, l, c, a, t), v in sorted(votos.items())
    ]

    # El total de positivos se calcula, porque el origen no lo trae como fila.
    positivos = {}
    for f in resultados:
        if f["tipo_registro"] == "agrupacion":
            k = (f["seccion"], f["localidad"], f["circuito_id"])
            positivos[k] = positivos.get(k, 0) + f["votos"]
    resultados += [
        {**comun, "seccion": s, "localidad": l, "circuito_id": c,
         "agrupacion": "POSITIVO", "tipo_registro": "positivo", "votos": v}
        for (s, l, c), v in sorted(positivos.items())
    ]

    conteo_mesas = {}
    for (s, l, _) in mesas:
        conteo_mesas[(s, l)] = conteo_mesas.get((s, l), 0) + 1
    metadatos = [
        {"anio": anio, "instancia": instancia, "fecha": comun["fecha"],
         "distrito": DISTRITO, "seccion": s, "localidad": l,
         "mesas": n, "electores": electores.get((s, l), 0),
         "recuento_tipo": "PROVISORIO", "archivo_origen": Path(ruta).name}
        for (s, l), n in sorted(conteo_mesas.items())
    ]
    return resultados, metadatos, sin_mapear


def main():
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    ruta, anio, instancia = sys.argv[1], sys.argv[2], sys.argv[3]
    resultados, metadatos, sin_mapear = agregar(ruta, anio, instancia)

    base = f"{anio}_{instancia}_localidad_desde_mesa"
    for nombre, filas, cols in ((f"{base}.csv", resultados, COLUMNAS),
                                (f"{base}_metadatos.csv", metadatos,
                                 COLUMNAS_META)):
        with open(SALIDA / nombre, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=cols)
            w.writeheader()
            w.writerows(filas)
        print(f"-> datos/procesados/{nombre} ({len(filas)} filas)")

    locs = {(m["seccion"], m["localidad"]) for m in metadatos}
    print(f"\n{len(locs)} localidades, "
          f"{sum(m['mesas'] for m in metadatos)} mesas, "
          f"{sum(m['electores'] for m in metadatos):,} electores")
    print(f"circuitos del archivo sin localidad asignada: {len(sin_mapear)} "
          f"(quedan fuera del recorte de 30 localidades)")


if __name__ == "__main__":
    main()
