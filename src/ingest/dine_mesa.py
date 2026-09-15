"""Ingesta del formato DINE a nivel mesa (`presentacionDeResultados`).

Es el formato que habilita la cobertura provincial completa. Una fila por
mesa x cargo x lista x tipo de voto, con estas columnas:

    año, eleccion_tipo, recuento_tipo, padron_tipo, distrito_id, distrito_nombre,
    seccionprovincial_id, seccion_id, seccion_nombre, circuito_id, circuito_nombre,
    mesa_id, mesa_tipo, mesa_electores, cargo_id, cargo_nombre, agrupacion_id,
    agrupacion_nombre, lista_numero, lista_nombre, votos_tipo, votos_cantidad

Tres cosas que definen el diseno de este modulo:

1. **`seccion_nombre` es el departamento.** Es decir que este formato da los 19
   departamentos sin necesidad de ningun nomenclador. Solo la localidad depende
   del mapeo circuito -> localidad.
2. Por eso, un circuito sin localidad conocida **no se descarta**: se imputa a
   SIN_ASIGNAR conservando su departamento, de modo que el total departamental
   siga siendo completo y correcto.
3. En las PASO cada agrupacion presenta varias listas internas. El total de la
   agrupacion es la suma de sus listas, asi que se agrupa por agrupacion y se
   suman las listas. Los electores, en cambio, se cuentan **una vez por mesa**:
   el dato se repite en cada fila de esa mesa y sumarlo tal cual lo multiplicaria
   por la cantidad de listas.
"""

from __future__ import annotations

import csv
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import comunes as c  # noqa: E402

DISTRITO_SANTA_FE = "21"

#: Como nombra la DINE cada instancia en la columna eleccion_tipo.
_INSTANCIA = {
    "PASO": "PASO",
    "PRIMARIA": "PASO",
    "PRIMARIAS": "PASO",
    "GENERAL": "GENERAL",
    "GENERALES": "GENERAL",
    "BALLOTAGE": "BALLOTAGE",
    "BALLOTTAGE": "BALLOTAGE",
    "SEGUNDA VUELTA": "BALLOTAGE",
}


@dataclass
class IngestaMesa:
    fuente: dict
    hechos: list[dict] = field(default_factory=list)
    padron: list[dict] = field(default_factory=list)
    circuitos: list[dict] = field(default_factory=list)
    resumen: dict = field(default_factory=dict)


def _norm(valor) -> str:
    return c.sin_acentos(str(valor or "")).upper().strip()


def _es_presidente(cargo: str) -> bool:
    t = _norm(cargo)
    return t.startswith("PRESIDENTE")


def _filas(ruta: Path):
    """Itera las filas del archivo, sea CSV o XLSX, como diccionarios."""
    ruta = Path(ruta)
    if ruta.suffix.lower() in (".csv", ".txt"):
        with open(ruta, newline="", encoding="utf-8-sig") as fh:
            yield from csv.DictReader(fh)
        return

    import openpyxl  # solo se necesita para el formato xlsx

    wb = openpyxl.load_workbook(ruta, read_only=True, data_only=True)
    ws = wb.worksheets[0]
    it = ws.iter_rows(values_only=True)
    encabezado = [str(h).strip() if h is not None else "" for h in next(it)]
    for fila in it:
        yield dict(zip(encabezado, fila))
    wb.close()


def leer_archivo(ruta: Path, nomenclador: dict[str, str] | None = None,
                 distrito: str = DISTRITO_SANTA_FE) -> IngestaMesa:
    """Lee un archivo a nivel mesa y lo agrega a nivel localidad.

    `nomenclador` mapea circuito_id -> localidad_id. Lo que no figure ahi queda
    en SIN_ASIGNAR, con su departamento correcto.
    """
    ruta = Path(ruta)
    nomenclador = nomenclador or {}

    votos: dict[tuple, int] = {}
    etiquetas: dict[str, str] = {}
    geo: dict[str, tuple[str, str, str, str]] = {}
    mesas_vistas: set[tuple] = set()
    electores: dict[str, int] = {}
    mesas_por_localidad: dict[str, int] = {}
    circuitos: dict[str, dict] = {}
    instancias: set[str] = set()
    recuentos: set[str] = set()
    anios: set[int] = set()
    circuitos_sin_localidad: set[str] = set()
    filas_leidas = 0

    for fila in _filas(ruta):
        filas_leidas += 1
        if str(fila.get("distrito_id", "")).strip() != distrito:
            continue
        if not _es_presidente(fila.get("cargo_nombre", "")):
            continue

        instancia = _INSTANCIA.get(_norm(fila.get("eleccion_tipo")))
        if instancia is None:
            raise ValueError(f"eleccion_tipo desconocido: {fila.get('eleccion_tipo')!r}")
        instancias.add(instancia)
        anios.add(int(fila["año"] if "año" in fila else fila["anio"]))
        recuentos.add(_norm(fila.get("recuento_tipo")) or "NO_DECLARADO")

        depto = c.normalizar_nombre(fila.get("seccion_nombre"))
        depto_id = c.clave(depto)
        circuito = c.normalizar_nombre(fila.get("circuito_id"))
        localidad_id = nomenclador.get(circuito)
        if localidad_id is None:
            # Se imputa al departamento, no a un cajon comun: mezclar
            # departamentos rompería el único nivel que este formato cubre
            # completo sin nomenclador.
            localidad_id = c.localidad_sin_asignar(depto_id)
            circuitos_sin_localidad.add(circuito)
        nombre_localidad = f"Sin asignar ({depto})" if c.es_sin_asignar(localidad_id) else localidad_id
        geo[localidad_id] = (depto_id, depto, localidad_id, nombre_localidad)
        circuitos.setdefault(circuito, {
            "circuito_id": circuito,
            "departamento_id": depto_id,
            "departamento": depto,
            "localidad_id": localidad_id,
        })

        tipo_voto = c.normalizar_tipo_voto(fila.get("votos_tipo"))
        nombre = c.normalizar_nombre(fila.get("agrupacion_nombre")) if tipo_voto == "POSITIVO" else None
        clave_agrupacion = c.clave(nombre) if nombre else None
        if clave_agrupacion:
            etiquetas[clave_agrupacion] = nombre

        llave = (localidad_id, tipo_voto, clave_agrupacion)
        votos[llave] = votos.get(llave, 0) + c.a_entero(fila.get("votos_cantidad"))

        # Los electores se cuentan una vez por mesa, no una vez por fila.
        mesa = (fila.get("seccion_id"), circuito, fila.get("mesa_id"))
        if mesa not in mesas_vistas:
            mesas_vistas.add(mesa)
            electores[localidad_id] = electores.get(localidad_id, 0) + c.a_entero(fila.get("mesa_electores"))
            mesas_por_localidad[localidad_id] = mesas_por_localidad.get(localidad_id, 0) + 1

    if len(instancias) != 1 or len(anios) != 1:
        raise ValueError(
            f"El archivo mezcla mas de una instancia: anios={sorted(anios)}, "
            f"instancias={sorted(instancias)}. Hay que separarlo antes de cargarlo.")

    elec = c.eleccion_id(anios.pop(), instancias.pop())
    recuento = "PROVISORIO" if "PROVISORIO" in recuentos else (
        "DEFINITIVO" if "DEFINITIVO" in recuentos else "NO_DECLARADO")
    fuente_id = f"MESA_{elec}"

    ing = IngestaMesa(fuente={
        "fuente_id": fuente_id,
        "archivo": ruta.name,
        "eleccion_id": elec,
        "organismo": "Dirección Nacional Electoral (DINE)",
        "archivo_origen": ruta.name,
        "unidad_original": "Mesa electoral",
        "recuento": recuento,
        "cobertura_declarada": f"{len({g[0] for g in geo.values()})} departamentos",
        "fecha_proceso_origen": None,
        "sha256": c.sha256_archivo(ruta),
        "observaciones": ("Recuento provisorio: reemplazar por el definitivo cuando exista."
                          if recuento == "PROVISORIO" else None),
    })

    for (localidad_id, tipo_voto, clave_agrupacion), cantidad in sorted(
            votos.items(), key=lambda kv: (kv[0][0], kv[0][1], kv[0][2] or "")):
        depto_id, depto, _loc_id, localidad = geo[localidad_id]
        ing.hechos.append({
            "eleccion_id": elec,
            "departamento_id": depto_id,
            "departamento": depto,
            "localidad_id": localidad_id,
            "localidad": localidad,
            "tipo_voto": tipo_voto,
            "agrupacion_key": clave_agrupacion,
            "agrupacion_nombre_fuente": etiquetas.get(clave_agrupacion) if clave_agrupacion else None,
            "formula": None,
            "votos": cantidad,
            "fuente_id": fuente_id,
        })

    for localidad_id, cantidad in sorted(electores.items()):
        depto_id = geo[localidad_id][0]
        ing.padron.append({
            "eleccion_id": elec,
            "departamento_id": depto_id,
            "localidad_id": localidad_id,
            "mesas": mesas_por_localidad[localidad_id],
            "electores": cantidad,
            "fuente_id": fuente_id,
        })

    for circuito in sorted(circuitos.values(), key=lambda d: d["circuito_id"]):
        ing.circuitos.append({**circuito, "eleccion_id": elec, "fuente_id": fuente_id,
                              "localidad": geo[circuito["localidad_id"]][3]})

    ing.resumen = {
        "filas_leidas": filas_leidas,
        "mesas": len(mesas_vistas),
        "departamentos": len({g[0] for g in geo.values()}),
        "circuitos": len(circuitos),
        "circuitos_sin_localidad": sorted(circuitos_sin_localidad),
    }
    return ing
