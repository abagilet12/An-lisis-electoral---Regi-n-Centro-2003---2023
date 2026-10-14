#!/usr/bin/env python3
"""
Cliente de la API de Publicacion de Resultados Electorales (DINE).

    https://resultados.mininterior.gob.ar/api/resultados/getResultados

No requiere token: el spec menciona autenticacion JWT como posibilidad, pero
las consultas de resultados historicos responden sin credenciales (verificado
2026-09-17).

Limites relevantes para este proyecto, comprobados contra la API:
  - Solo hay datos desde 2011. 2003 y 2007 devuelven vacio.
  - Devuelve el RECUENTO PROVISIONAL, que no coincide con el escrutinio
    definitivo de la Justicia Nacional Electoral (ver docs/API_DINE.md).
  - Los ids de ambito NO son estables entre anios: seccionId=1 es un
    departamento chico en 2011-2019 y La Capital en 2023.
  - Consultando el distrito sin seccion, las PASO devuelven un total
    parcial. Para el total provincial hay que pedir las 19 secciones y
    sumar (ver total_provincial).

Uso:
    python3 scripts/cliente_api_dine.py 2023 2 > salida.json
"""
import json
import sys
import time
import urllib.parse
import urllib.request

BASE = "https://resultados.mininterior.gob.ar/api/resultados/getResultados"

SANTA_FE = "21"
PRESIDENTE = 1
PROVISIONAL = "1"
INSTANCIAS = {1: "PASO", 2: "GENERAL", 3: "BALOTAJE"}

# Santa Fe tiene 19 departamentos. Los ids son 1..19 en 2023; en anios
# anteriores el mapeo id->departamento cambia, asi que hay que reconstruirlo
# por anio antes de comparar series.
SECCIONES_SANTA_FE = range(1, 20)


def consultar(anio, tipo_eleccion, seccion_id=None, circuito_id=None,
              distrito_id=SANTA_FE, categoria_id=PRESIDENTE, reintentos=3):
    params = {
        "anioEleccion": str(anio),
        "tipoRecuento": PROVISIONAL,
        "tipoEleccion": str(tipo_eleccion),
        "categoriaId": str(categoria_id),
        "distritoId": distrito_id,
    }
    if seccion_id is not None:
        params["seccionId"] = str(seccion_id)
    if circuito_id is not None:
        params["circuitoId"] = str(circuito_id)

    url = f"{BASE}?{urllib.parse.urlencode(params)}"
    for intento in range(reintentos):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                return json.load(r)
        except Exception:
            if intento == reintentos - 1:
                raise
            time.sleep(2 ** intento)


def tiene_datos(respuesta):
    return bool(respuesta and respuesta["estadoRecuento"]["mesasTotalizadas"])


def total_provincial(anio, tipo_eleccion):
    """Recorre las 19 secciones y devuelve una fila por agrupacion.

    Se suma por seccion en vez de pedir el distrito directamente porque en
    las PASO la consulta a nivel distrito devuelve un total parcial.
    """
    votos, mesas, electores, votantes = {}, 0, 0, 0
    for seccion in SECCIONES_SANTA_FE:
        r = consultar(anio, tipo_eleccion, seccion_id=seccion)
        if not tiene_datos(r):
            continue
        estado = r["estadoRecuento"]
        mesas += estado["mesasTotalizadas"]
        electores += estado["cantidadElectores"]
        votantes += estado["cantidadVotantes"]
        for a in r["valoresTotalizadosPositivos"]:
            votos[a["nombreAgrupacion"]] = (
                votos.get(a["nombreAgrupacion"], 0) + a["votos"]
            )
    return {
        "anio": anio,
        "instancia": INSTANCIAS[tipo_eleccion],
        "mesas": mesas,
        "electores": electores,
        "votantes": votantes,
        "agrupaciones": dict(sorted(votos.items(), key=lambda kv: -kv[1])),
    }


if __name__ == "__main__":
    anio, tipo = int(sys.argv[1]), int(sys.argv[2])
    print(json.dumps(total_provincial(anio, tipo), ensure_ascii=False, indent=2))
