#!/usr/bin/env python3
"""
Incorpora fuentes transcriptas a mano, para años que ningún organismo publica
en formato procesable.

Hoy solo aplica a la general de 2003: la DINE no tiene datos anteriores a
2011 y la Consulta de Escrutinio por Zona tampoco la cubre, así que el único
registro disponible es una tabla de resultados que hubo que transcribir.

Cada archivo de `datos/crudos/transcripciones/` es autocontenido: trae las
fórmulas y las filas de cierre de la fuente original, de modo que la
transcripción se puede verificar sin volver a la fuente. Este script hace
esa verificación en cada corrida.

Salida: datos/procesados/resultados_provincia_transcripto.csv
"""
import csv
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CRUDOS = RAIZ / "datos" / "crudos" / "transcripciones"
SALIDA = RAIZ / "datos" / "procesados"

CARGO, DISTRITO_ID, DISTRITO = "PRESIDENTE Y VICE", "21", "Santa Fe"
FECHAS = {("2003", "GENERAL"): "2003-04-27"}

COLUMNAS = ["anio", "instancia", "fecha", "cargo", "distrito_id", "distrito",
            "agrupacion", "formula", "tipo_registro", "votos", "pct",
            "recuento_tipo", "archivo_origen"]


def parsear(archivo):
    m = re.match(r"(\d{4})_([A-Z]+)_", archivo.name)
    anio, instancia = m.group(1), m.group(2)
    comun = {"anio": anio, "instancia": instancia,
             "fecha": FECHAS.get((anio, instancia), ""), "cargo": CARGO,
             "distrito_id": DISTRITO_ID, "distrito": DISTRITO,
             "recuento_tipo": "DEFINITIVO", "archivo_origen": archivo.name}
    return [{**comun, "agrupacion": r["agrupacion"], "formula": r["formula"],
             "tipo_registro": r["tipo_registro"],
             "votos": float(r["votos"]), "pct": r["pct"]}
            for r in csv.DictReader(open(archivo, encoding="utf-8"))]


def verificar(filas, archivo):
    """Comprueba la transcripción contra las propias filas de cierre."""
    def valor(tipo):
        return next((f["votos"] for f in filas if f["tipo_registro"] == tipo),
                    None)

    avisos = []
    suma = sum(f["votos"] for f in filas if f["tipo_registro"] == "agrupacion")
    positivo, blancos = valor("positivo"), valor("blancos")
    nulos, total = valor("nulos"), valor("total")
    padron, participacion = valor("inscriptos"), valor("participacion")

    if positivo is not None and suma != positivo:
        avisos.append(f"{archivo}: fórmulas suman {suma:,.0f} != "
                      f"positivos {positivo:,.0f}")
    if None not in (positivo, blancos, nulos, total):
        if positivo + blancos + nulos != total:
            avisos.append(f"{archivo}: positivos+blancos+nulos "
                          f"{positivo + blancos + nulos:,.0f} != "
                          f"total {total:,.0f}")
    if None not in (total, padron, participacion):
        calc = 100 * total / padron
        if abs(calc - participacion) > 0.01:
            avisos.append(f"{archivo}: participación calculada {calc:.2f}% != "
                          f"declarada {participacion:.2f}%")
    return avisos


def main():
    archivos = sorted(CRUDOS.glob("*.csv"))
    if not archivos:
        sys.exit(f"no hay transcripciones en {CRUDOS}")

    filas, avisos = [], []
    for archivo in archivos:
        parseadas = parsear(archivo)
        avisos += verificar(parseadas, archivo.name)
        filas += parseadas
        n = sum(1 for f in parseadas if f["tipo_registro"] == "agrupacion")
        print(f"  {archivo.name[:50]:50} {n} fórmulas")

    SALIDA.mkdir(parents=True, exist_ok=True)
    destino = SALIDA / "resultados_provincia_transcripto.csv"
    with open(destino, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNAS)
        w.writeheader()
        w.writerows(filas)
    print(f"-> datos/procesados/{destino.name} ({len(filas)} filas)")

    if avisos:
        print("\nControles de consistencia:")
        for a in avisos:
            print("  !", a)
    else:
        print("\nControles de consistencia: OK "
              "(fórmulas vs positivos, componentes vs total, participación).")


if __name__ == "__main__":
    main()
