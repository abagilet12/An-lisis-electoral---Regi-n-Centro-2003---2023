#!/usr/bin/env python3
"""
Integra el CSV consolidado que produce notebooks/extraccion_api_dine.ipynb.

Aporta el nivel DEPARTAMENTO (la API lo llama "seccion") para 2011, 2015,
2019 y 2023, cubriendo la provincia entera. Es el nivel intermedio que a la
base le faltaba: hasta ahora `provincia_completa` solo tenia 2003 y 2023.

Dos advertencias que el parser deja asentadas en los datos:

1. Es RECUENTO PROVISORIO. Contrastado contra el escrutinio definitivo en la
   general 2023: 18.456 votos menos (-0,90 %). No mezclar con el nivel
   provincial de la base, que usa definitivo.
2. En 2011 la provincia viene partida en 22 unidades y no en los 19
   departamentos. El padron total cierra exacto contra el archivo oficial
   (2.440.284 electores), asi que la particion es completa, pero sus unidades
   NO son los departamentos de los demas anios y no deben cruzarse con ellos.

Del nivel circuito solo se conserva 2023, y unicamente para control: ese dato
ya esta en la base, sacado del archivo por mesa.

Salida: datos/procesados/resultados_departamento.csv
"""
import csv
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ORIGEN = RAIZ / "datos" / "crudos" / "api_dine" / "api_dine_santa_fe_consolidado.csv"
SALIDA = RAIZ / "datos" / "procesados"

CARGO, DISTRITO_ID, DISTRITO = "PRESIDENTE Y VICE", "21", "Santa Fe"

# Anios cuya particion en "secciones" NO coincide con los 19 departamentos.
PARTICION_ANOMALA = {"2011"}

COLUMNAS = ["anio", "instancia", "cargo", "distrito_id", "distrito",
            "seccion_id", "mesas", "electores", "votantes", "agrupacion",
            "lista", "tipo_registro", "votos", "recuento_tipo", "fuente",
            "particion_comparable"]


def main():
    if not ORIGEN.exists():
        sys.exit(f"falta {ORIGEN}")

    filas = []
    for r in csv.DictReader(open(ORIGEN, encoding="utf-8")):
        if r["nivel"] != "seccion":      # el circuito ya esta en la base
            continue
        filas.append({
            "anio": r["anio"], "instancia": r["instancia"], "cargo": CARGO,
            "distrito_id": DISTRITO_ID, "distrito": DISTRITO,
            "seccion_id": r["seccion_id"],
            "mesas": int(r["mesas"]), "electores": int(r["electores"]),
            "votantes": int(r["votantes"]),
            "agrupacion": r["agrupacion"], "lista": r.get("lista", ""),
            "tipo_registro": r["tipo_registro"], "votos": int(r["votos"]),
            "recuento_tipo": "PROVISORIO", "fuente": "api_dine",
            # Marca si las unidades de ese anio son los 19 departamentos.
            "particion_comparable": ("no" if r["anio"] in PARTICION_ANOMALA
                                     else "si"),
        })

    destino = SALIDA / "resultados_departamento.csv"
    with open(destino, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNAS)
        w.writeheader()
        w.writerows(filas)
    print(f"-> datos/procesados/{destino.name} ({len(filas)} filas)")

    # Control: el padron no debe multiplicarse al sumar, asi que se toma una
    # sola fila por unidad.
    vistas, resumen = set(), {}
    for f in filas:
        clave = (f["anio"], f["instancia"], f["seccion_id"])
        if clave in vistas:
            continue
        vistas.add(clave)
        k = (f["anio"], f["instancia"])
        d = resumen.setdefault(k, {"u": 0, "mesas": 0, "electores": 0})
        d["u"] += 1
        d["mesas"] += f["mesas"]
        d["electores"] += f["electores"]

    orden = {"PASO": 0, "GENERAL": 1, "BALOTAJE": 2}
    print(f"\n{'elección':18} {'unid.':>6} {'mesas':>8} {'electores':>11}")
    for k in sorted(resumen, key=lambda x: (x[0], orden[x[1]])):
        d = resumen[k]
        aviso = "  <- no son los 19 departamentos" if k[0] in PARTICION_ANOMALA else ""
        print(f"  {k[0]} {k[1]:10} {d['u']:>6} {d['mesas']:>8,} "
              f"{d['electores']:>11,}{aviso}")


if __name__ == "__main__":
    main()
