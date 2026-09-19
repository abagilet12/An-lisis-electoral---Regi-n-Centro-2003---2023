#!/usr/bin/env python3
"""
Une las dos fuentes de nivel localidad en una sola tabla:

  resultados_localidad.csv            <- los .xlsx "Votos por Localidad"
  *_localidad_desde_mesa.csv          <- agregado desde el CSV por mesa

Ambas comparten esquema. La columna `fuente` deja asentado de donde sale
cada fila, y `recuento_tipo` si es provisorio o definitivo, para que no se
mezclen sin querer al comparar.

Salida: datos/procesados/serie_localidad.csv
"""
import csv
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SALIDA = RAIZ / "datos" / "procesados"

COLUMNAS = ["anio", "instancia", "fecha", "cargo", "distrito_id", "distrito",
            "seccion", "localidad", "circuito_id", "agrupacion",
            "tipo_registro", "votos", "recuento_tipo", "fuente"]


def leer(ruta, fuente, recuento_por_defecto):
    filas = []
    for r in csv.DictReader(open(ruta, encoding="utf-8")):
        filas.append({
            **{c: r.get(c, "") for c in COLUMNAS},
            "recuento_tipo": r.get("recuento_tipo") or recuento_por_defecto,
            "fuente": fuente,
        })
    return filas


def main():
    filas = leer(SALIDA / "resultados_localidad.csv", "xlsx_votos_por_localidad",
                 "NO DECLARADO")
    for ruta in sorted(SALIDA.glob("*_localidad_desde_mesa.csv")):
        filas += leer(ruta, "csv_por_mesa", "PROVISORIO")

    with open(SALIDA / "serie_localidad.csv", "w", newline="",
              encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNAS)
        w.writeheader()
        w.writerows(sorted(filas, key=lambda f: (f["anio"], f["instancia"],
                                                 f["seccion"], f["localidad"],
                                                 f["agrupacion"])))
    print(f"-> datos/procesados/serie_localidad.csv ({len(filas)} filas)")

    cobertura = {}
    for f in filas:
        cobertura.setdefault((f["anio"], f["instancia"]), f["fuente"])
    print(f"\n{len(cobertura)} instancias:")
    for (anio, inst), fuente in sorted(cobertura.items()):
        print(f"  {anio} {inst:9} {fuente}")


if __name__ == "__main__":
    main()
