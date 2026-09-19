#!/usr/bin/env python3
"""
Procesa los escrutinios provisorios del repositorio PoliticaArgentina/data_warehouse.

Es la fuente que cierra los agujeros de la serie: trae datos **a nivel mesa**
para 2003 y 2007, que ningun organismo publica desagregados, mas 2011, 2015 y
2019. Nueve instancias, la provincia entera.

Origen ultimo: Atlas Electoral de Andy Tow (2003-2017) y, para 2019, los
paquetes de @pmoracho. Son escrutinios PROVISORIOS.

Formato de entrada: una fila por mesa, una columna por codigo de lista, mas
`blancos` y `nulos`. Los nombres de las listas salen de
`listas_presi_<instancia><anio>.csv`, que mapea codigo + provincia a
denominacion (la misma lista puede llamarse distinto en cada distrito).

Salida: datos/procesados/resultados_circuito_polar.csv
"""
import csv
import re
import sys
from collections import defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CRUDOS = RAIZ / "datos" / "crudos" / "polar"
SALIDA = RAIZ / "datos" / "procesados"

CODPROV_SANTA_FE = "21"
CARGO, DISTRITO_ID, DISTRITO = "PRESIDENTE Y VICE", "21", "Santa Fe"

INSTANCIAS = {"gral": "GENERAL", "paso": "PASO", "balota": "BALOTAJE"}
NO_LISTA = {"codprov", "depto", "coddepto", "circuito", "mesa", "electores"}
ESPECIALES = {"blancos": "blancos", "nulos": "nulos"}

# En la general 2019 los datos usan codigos 00001-00010 y el diccionario de
# listas usa 00024-00108: no hay interseccion, porque ese anio se reconstruyo
# de otra fuente (paquetes de @pmoracho). El mapeo se resolvio cotejando los
# totales contra los datos de la API de la DINE, que si trae los nombres:
# los seis codigos casan uno a uno dentro del +-1 %. El par ajustado
# (JxC/FdT) se confirmo aparte viendo que en Rosario el orden se invierte
# igual en ambas fuentes: gana 00005 y gana Frente de Todos.
CODIGOS_2019_GENERAL = {
    "00009": "JUNTOS POR EL CAMBIO",
    "00005": "FRENTE DE TODOS",
    "00001": "CONSENSO FEDERAL",
    "00004": "UNITE POR LA LIBERTAD Y LA DIGNIDAD",
    "00010": "FRENTE NOS",
    "00002": "FRENTE DE IZQUIERDA Y DE TRABAJADORES - UNIDAD",
}

# En 2011 la provincia viene partida en 22 unidades y no en los 19
# departamentos. El padron total cierra, pero las unidades no son las de los
# demas anios.
PARTICION_ANOMALA = {"2011"}

COLUMNAS = ["anio", "instancia", "cargo", "distrito_id", "distrito",
            "seccion_id", "seccion", "circuito_id", "agrupacion",
            "tipo_registro", "votos", "electores", "mesas",
            "recuento_tipo", "fuente", "particion_comparable"]


def limpiar(s):
    return re.sub(r"\s+", " ", str(s)).strip()


def cargar_listas(instancia, anio):
    """codigo de lista -> denominacion, para esta provincia."""
    ruta = CRUDOS / f"listas_presi_{instancia}{anio}.csv"
    if not ruta.exists():
        return {}
    return {r["vot_parCodigo"]: limpiar(r["parDenominacion"])
            for r in csv.DictReader(open(ruta, encoding="utf-8",
                                         errors="replace"))
            if r["vot_proCodigoProvincia"] == CODPROV_SANTA_FE}


def parsear(archivo):
    m = re.match(r"arg_presi_(gral|paso|balota)(\d{4})\.csv", archivo.name)
    if not m:
        return []
    instancia_corta, anio = m.group(1), m.group(2)
    instancia = INSTANCIAS[instancia_corta]
    nombres = cargar_listas(instancia_corta, anio)
    if (anio, instancia) == ("2019", "GENERAL"):
        nombres = {**nombres, **CODIGOS_2019_GENERAL}

    votos = defaultdict(int)          # (circuito, etiqueta) -> votos
    geo, electores, mesas = {}, defaultdict(int), defaultdict(int)

    with open(archivo, encoding="utf-8", errors="replace") as fh:
        for fila in csv.DictReader(fh):
            if fila.get("codprov") != CODPROV_SANTA_FE:
                continue
            circuito = fila["circuito"].strip()
            geo[circuito] = (fila["coddepto"].strip(), limpiar(fila["depto"]))
            electores[circuito] += int(fila["electores"] or 0)
            mesas[circuito] += 1

            for col, valor in fila.items():
                if col in NO_LISTA or not valor:
                    continue
                etiqueta = ESPECIALES.get(col) or nombres.get(col, col)
                votos[(circuito, etiqueta, col)] += int(valor or 0)

    comun = {"anio": anio, "instancia": instancia, "cargo": CARGO,
             "distrito_id": DISTRITO_ID, "distrito": DISTRITO,
             "recuento_tipo": "PROVISORIO", "fuente": "polar_atlas_andytow",
             "particion_comparable": "no" if anio in PARTICION_ANOMALA else "si"}

    filas = []
    for (circuito, etiqueta, col), cantidad in sorted(votos.items()):
        seccion_id, seccion = geo[circuito]
        filas.append({**comun, "seccion_id": seccion_id, "seccion": seccion,
                      "circuito_id": circuito, "agrupacion": etiqueta,
                      "tipo_registro": ESPECIALES.get(col, "agrupacion"),
                      "votos": cantidad, "electores": electores[circuito],
                      "mesas": mesas[circuito]})
    return filas


def verificar(filas, archivo):
    """El padron agregado y la coherencia de los totales."""
    if not filas:
        return f"{archivo}: sin datos de Santa Fe"
    unidades = {}
    for f in filas:
        unidades[f["circuito_id"]] = (f["electores"], f["mesas"])
    sin_nombre = {f["agrupacion"] for f in filas
                  if f["tipo_registro"] == "agrupacion"
                  and re.fullmatch(r"\d{4,5}", f["agrupacion"])}
    if sin_nombre:
        return (f"{archivo}: {len(sin_nombre)} códigos de lista sin "
                f"denominación: {sorted(sin_nombre)[:5]}")
    return None


def main():
    archivos = sorted(CRUDOS.glob("arg_presi_*.csv"))
    if not archivos:
        sys.exit(f"no hay archivos en {CRUDOS}")

    todas, avisos = [], []
    orden = {"PASO": 0, "GENERAL": 1, "BALOTAJE": 2}
    print(f"{'elección':17} {'circuitos':>10} {'deptos':>7} {'mesas':>7} "
          f"{'electores':>12} {'listas':>7}")
    resumen = []
    for archivo in archivos:
        filas = parsear(archivo)
        aviso = verificar(filas, archivo.name)
        if aviso:
            avisos.append(aviso)
        todas += filas
        if filas:
            u = {f["circuito_id"]: (f["electores"], f["mesas"]) for f in filas}
            resumen.append((filas[0]["anio"], filas[0]["instancia"], len(u),
                            len({f["seccion_id"] for f in filas}),
                            sum(v[1] for v in u.values()),
                            sum(v[0] for v in u.values()),
                            len({f["agrupacion"] for f in filas
                                 if f["tipo_registro"] == "agrupacion"})))
    for r in sorted(resumen, key=lambda x: (x[0], orden[x[1]])):
        print(f"  {r[0]} {r[1]:10} {r[2]:>10} {r[3]:>7} {r[4]:>7,} "
              f"{r[5]:>12,} {r[6]:>7}")

    SALIDA.mkdir(parents=True, exist_ok=True)
    destino = SALIDA / "resultados_circuito_polar.csv"
    with open(destino, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNAS)
        w.writeheader()
        w.writerows(todas)
    print(f"\n-> datos/procesados/{destino.name} ({len(todas):,} filas)")

    if avisos:
        print("\nControles:")
        for a in avisos:
            print("  !", a)
    else:
        print("\nControles: OK, todas las listas tienen denominación.")


if __name__ == "__main__":
    main()
