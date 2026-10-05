#!/usr/bin/env python3
"""
Agrega el CSV por mesa de la DINE a nivel CIRCUITO, para toda la provincia.

El circuito es la unidad geografica del mapa electoral y viene identificado
en el propio archivo, asi que este agregado no depende de ningun nomenclador
y cubre los 523 circuitos de Santa Fe, no solo los de la zona nucleo.

Emite ademas el nomenclador de circuitos: codigo, departamento, padron y
mesas, con la localidad cuando se conoce. Las filas sin localidad son
exactamente las que faltan relevar a mano.

ATENCION: estos archivos son del RECUENTO PROVISORIO (ver
docs/NOTA_METODOLOGICA_2023.md).

Uso:
    python3 scripts/agregar_mesa_a_circuito.py <csv> <anio> <instancia>
"""
import csv
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SALIDA = RAIZ / "datos" / "procesados"
NOMENCLADOR_LOCALIDAD = SALIDA / "nomenclador_circuito_localidad.csv"

CARGO_PRESIDENTE = "1"
CARGO = "PRESIDENTE Y VICE"
DISTRITO_ID, DISTRITO = "21", "Santa Fe"
FECHAS = {("2023", "PASO"): "2023-08-13", ("2023", "GENERAL"): "2023-10-22",
          ("2023", "BALOTAJE"): "2023-11-19"}
TIPOS_VOTO = {"EN BLANCO": "blancos", "NULO": "nulos",
              "IMPUGNADO": "impugnados", "RECURRIDO": "recurridos",
              "COMANDO": "comando"}

COLUMNAS = ["anio", "instancia", "fecha", "cargo", "distrito_id", "distrito",
            "seccion_id", "seccion", "circuito_id", "localidad", "agrupacion",
            "tipo_registro", "votos", "recuento_tipo", "archivo_origen"]
COLUMNAS_NOM = ["circuito_id", "seccion_id", "seccion", "localidad",
                "mesas", "electores", "anio_referencia"]


def clave(c):
    return str(c).strip().lstrip("0")


def localidades_conocidas(anio):
    if not NOMENCLADOR_LOCALIDAD.exists():
        return {}
    return {clave(r["circuito_id"]): r["localidad"]
            for r in csv.DictReader(open(NOMENCLADOR_LOCALIDAD,
                                         encoding="utf-8"))
            if r["anio"] == anio}


def agregar(ruta, anio, instancia):
    loc = localidades_conocidas(anio)
    votos, geo, mesas_vistas, electores, mesas = {}, {}, set(), {}, {}

    with open(ruta, encoding="utf-8") as fh:
        for fila in csv.DictReader(fh):
            if fila["cargo_id"] != CARGO_PRESIDENTE:
                continue
            circuito = fila["circuito_id"].strip()
            geo[circuito] = (fila["seccion_id"], fila["seccion_nombre"])

            tipo = fila["votos_tipo"]
            etiqueta = (fila["agrupacion_nombre"] if tipo == "POSITIVO"
                        else tipo)
            registro = ("agrupacion" if tipo == "POSITIVO"
                        else TIPOS_VOTO.get(tipo, tipo.lower()))
            k = (circuito, etiqueta, registro)
            votos[k] = votos.get(k, 0) + int(fila["votos_cantidad"] or 0)

            # El padron de cada mesa se cuenta una sola vez.
            mesa = (circuito, fila["mesa_id"])
            if mesa not in mesas_vistas:
                mesas_vistas.add(mesa)
                electores[circuito] = (electores.get(circuito, 0)
                                       + int(fila["mesa_electores"] or 0))
                mesas[circuito] = mesas.get(circuito, 0) + 1

    comun = {"anio": anio, "instancia": instancia,
             "fecha": FECHAS.get((anio, instancia), ""), "cargo": CARGO,
             "distrito_id": DISTRITO_ID, "distrito": DISTRITO,
             "recuento_tipo": "PROVISORIO", "archivo_origen": Path(ruta).name}

    def fila_salida(circuito, etiqueta, registro, cantidad):
        seccion_id, seccion = geo[circuito]
        return {**comun, "seccion_id": seccion_id, "seccion": seccion,
                "circuito_id": circuito,
                "localidad": loc.get(clave(circuito), ""),
                "agrupacion": etiqueta, "tipo_registro": registro,
                "votos": cantidad}

    resultados = [fila_salida(c, e, r, v)
                  for (c, e, r), v in sorted(votos.items())]

    # El total de positivos no viene como fila en el origen: se calcula.
    positivos = {}
    for f in resultados:
        if f["tipo_registro"] == "agrupacion":
            positivos[f["circuito_id"]] = (positivos.get(f["circuito_id"], 0)
                                           + f["votos"])
    resultados += [fila_salida(c, "POSITIVO", "positivo", v)
                   for c, v in sorted(positivos.items())]

    nomenclador = [{"circuito_id": c, "seccion_id": geo[c][0],
                    "seccion": geo[c][1], "localidad": loc.get(clave(c), ""),
                    "mesas": mesas[c], "electores": electores[c],
                    "anio_referencia": anio}
                   for c in sorted(geo)]
    return resultados, nomenclador


def main():
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    ruta, anio, instancia = sys.argv[1], sys.argv[2], sys.argv[3]
    resultados, nomenclador = agregar(ruta, anio, instancia)

    for nombre, filas, cols in (
        (f"{anio}_{instancia}_circuito.csv", resultados, COLUMNAS),
        (f"nomenclador_circuitos_{anio}.csv", nomenclador, COLUMNAS_NOM),
    ):
        with open(SALIDA / nombre, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=cols)
            w.writeheader()
            w.writerows(filas)
        print(f"-> datos/procesados/{nombre} ({len(filas)} filas)")

    con = sum(1 for n in nomenclador if n["localidad"])
    print(f"\n{len(nomenclador)} circuitos, "
          f"{len({n['seccion'] for n in nomenclador})} departamentos, "
          f"{sum(n['mesas'] for n in nomenclador):,} mesas, "
          f"{sum(n['electores'] for n in nomenclador):,} electores")
    print(f"con localidad asignada: {con} | a relevar: {len(nomenclador) - con}")


if __name__ == "__main__":
    main()
