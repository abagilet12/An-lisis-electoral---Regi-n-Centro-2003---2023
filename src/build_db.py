"""Construye la base de datos a partir de las fuentes en data/raw/.

Salidas en data/processed/:
  santafe_presidenciales_2003_2023.csv  tabla de hechos (formato largo)
  dim_eleccion.csv / dim_localidad.csv / dim_circuito.csv / dim_agrupacion.csv
  padron.csv / fuentes.csv / incidencias.csv
  santafe_electoral.db                  SQLite con todo lo anterior

Se ejecuta siempre desde cero: no hay estado acumulado entre corridas.
"""

from __future__ import annotations

import csv
import sqlite3
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

import comunes as c  # noqa: E402
from ingest.control_provincial import leer_libro as leer_control  # noqa: E402
from ingest.derivados_xlsx import leer_libro  # noqa: E402
from nomenclador.colores import leer as leer_colores  # noqa: E402
from nomenclador.departamentos import leer as leer_departamentos  # noqa: E402

CRUDO = RAIZ / "data" / "raw"
SALIDA = RAIZ / "data" / "processed"

CAMPOS_HECHOS = [
    "eleccion_id", "anio", "instancia", "departamento_id", "departamento",
    "localidad_id", "localidad", "tipo_voto", "agrupacion_key",
    "agrupacion_nombre_fuente", "formula", "votos", "fuente_id",
]


def _escribir_csv(ruta: Path, campos: list[str], filas: list[dict]) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with open(ruta, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=campos, extrasaction="ignore")
        w.writeheader()
        for fila in filas:
            w.writerow(fila)


def _archivos_derivados() -> list[Path]:
    return sorted(CRUDO.glob("Votos por Localidad*.xlsx"))


def _archivos_control() -> list[Path]:
    """Planillas DINE por distrito: todo .xlsx que no sea un derivado."""
    derivados = {r.name for r in _archivos_derivados()}
    return sorted(r for r in CRUDO.glob("*.xlsx") if r.name not in derivados)


def _archivos_ambitos() -> list[Path]:
    return sorted(CRUDO.glob("AmbitosElectorales*.csv"))


def _archivos_colores() -> list[Path]:
    return sorted(CRUDO.glob("Colores_*.csv"))


def construir() -> dict:
    hechos: list[dict] = []
    padron: list[dict] = []
    circuitos: list[dict] = []
    fuentes: list[dict] = []
    incidencias: list[dict] = []

    archivos = _archivos_derivados()
    for ruta in archivos:
        ing = leer_libro(ruta)
        elec = ing.fuente["eleccion_id"]
        anio, instancia = elec.split("-")
        for h in ing.hechos:
            h["anio"] = int(anio)
            h["instancia"] = instancia
        hechos.extend(ing.hechos)
        padron.extend(ing.padron)
        circuitos.extend(ing.circuitos)
        fuentes.append(ing.fuente)
        incidencias.extend(ing.incidencias)

    # --- Totales de control (no entran en la serie) ------------------------
    control_totales: list[dict] = []
    control_padron: list[dict] = []
    hojas_omitidas: list[dict] = []
    for ruta in _archivos_control():
        controles, omitidas = leer_control(ruta)
        hojas_omitidas.extend(omitidas)
        for ctrl in controles:
            control_totales.extend(ctrl.totales)
            control_padron.extend(ctrl.padron)

    # --- Departamentos oficiales ------------------------------------------
    departamentos: dict[str, dict] = {}
    for ruta in _archivos_ambitos():
        for depto in leer_departamentos(ruta):
            departamentos.setdefault(depto["departamento_id"], depto)

    # --- Colores oficiales por agrupacion ---------------------------------
    colores: list[dict] = []
    for ruta in _archivos_colores():
        colores.extend(leer_colores(ruta))

    # --- Dimensiones ------------------------------------------------------
    localidades: dict[str, dict] = {}
    for h in hechos:
        localidades.setdefault(h["localidad_id"], {
            "localidad_id": h["localidad_id"],
            "localidad": h["localidad"],
            "departamento_id": h["departamento_id"],
            "departamento": h["departamento"],
        })

    # Un circuito puede repetirse entre anios; se guarda una fila por
    # (circuito, eleccion) para poder ver renumeraciones sin perder historia.
    circuitos_unicos: dict[tuple, dict] = {}
    for cir in circuitos:
        circuitos_unicos[(cir["circuito_id"], cir["eleccion_id"])] = cir

    agrupaciones: dict[tuple, dict] = {}
    for h in hechos:
        if not h["agrupacion_key"]:
            continue
        llave = (h["agrupacion_key"], h["eleccion_id"])
        agrupaciones.setdefault(llave, {
            "agrupacion_key": h["agrupacion_key"],
            "eleccion_id": h["eleccion_id"],
            "nombre_fuente": h["agrupacion_nombre_fuente"],
            "formula": h["formula"],
            "etiqueta_tipo": c.ETIQUETA_POR_ELECCION[h["eleccion_id"]],
            # Se completa en la etapa de unificacion de espacios politicos.
            "espacio_politico": None,
        })

    elecciones_cargadas = {h["eleccion_id"] for h in hechos}
    dim_eleccion = []
    for elec, (fecha, orden, nota) in c.CALENDARIO.items():
        anio, instancia = elec.split("-")
        dim_eleccion.append({
            "eleccion_id": elec,
            "anio": int(anio),
            "instancia": instancia,
            "fecha": fecha,
            "orden_cronologico": orden,
            "cargada": int(elec in elecciones_cargadas),
            "nota": nota,
        })

    # --- Escritura --------------------------------------------------------
    hechos.sort(key=lambda h: (c.CALENDARIO[h["eleccion_id"]][1], h["departamento_id"],
                               h["localidad_id"], h["tipo_voto"], h["agrupacion_key"] or ""))
    _escribir_csv(SALIDA / "santafe_presidenciales_2003_2023.csv", CAMPOS_HECHOS, hechos)
    _escribir_csv(SALIDA / "dim_eleccion.csv",
                  ["eleccion_id", "anio", "instancia", "fecha", "orden_cronologico", "cargada", "nota"],
                  dim_eleccion)
    _escribir_csv(SALIDA / "dim_departamento.csv",
                  ["departamento_id", "departamento", "codigo_dine", "distrito_id", "distrito",
                   "anio_nomenclador"],
                  sorted(departamentos.values(), key=lambda d: d["codigo_dine"]))
    _escribir_csv(SALIDA / "dim_color_agrupacion.csv",
                  ["anio", "agrupacion_id_dine", "agrupacion_key", "nombre_fuente", "color",
                   "distrito_id"],
                  colores)
    _escribir_csv(SALIDA / "control_totales.csv",
                  ["eleccion_id", "ambito", "distrito", "tipo_voto", "agrupacion_key",
                   "nombre_fuente", "formula", "votos", "fuente_id"],
                  control_totales)
    _escribir_csv(SALIDA / "control_padron.csv",
                  ["eleccion_id", "ambito", "distrito", "electores", "mesas", "votantes", "fuente_id"],
                  control_padron)
    _escribir_csv(SALIDA / "dim_localidad.csv",
                  ["localidad_id", "localidad", "departamento_id", "departamento"],
                  sorted(localidades.values(), key=lambda d: (d["departamento_id"], d["localidad_id"])))
    _escribir_csv(SALIDA / "dim_circuito.csv",
                  ["circuito_id", "eleccion_id", "departamento_id", "departamento", "localidad_id",
                   "localidad", "fuente_id"],
                  sorted(circuitos_unicos.values(), key=lambda d: (d["eleccion_id"], d["circuito_id"])))
    _escribir_csv(SALIDA / "dim_agrupacion.csv",
                  ["agrupacion_key", "eleccion_id", "nombre_fuente", "formula", "etiqueta_tipo",
                   "espacio_politico"],
                  sorted(agrupaciones.values(), key=lambda d: (d["eleccion_id"], d["agrupacion_key"])))
    _escribir_csv(SALIDA / "padron.csv",
                  ["eleccion_id", "departamento_id", "localidad_id", "mesas", "electores", "fuente_id"],
                  padron)
    _escribir_csv(SALIDA / "fuentes.csv",
                  ["fuente_id", "archivo", "eleccion_id", "organismo", "archivo_origen",
                   "unidad_original", "recuento", "cobertura_declarada", "fecha_proceso_origen",
                   "sha256", "observaciones"],
                  fuentes)
    _escribir_csv(SALIDA / "incidencias.csv",
                  ["eleccion_id", "localidad_id", "control", "esperado", "obtenido", "diferencia"],
                  incidencias)

    _armar_sqlite()

    return {
        "archivos": len(archivos),
        "archivos_control": len(_archivos_control()),
        "departamentos_nomenclador": len(departamentos),
        "control_filas": len(control_totales),
        "colores": len(colores),
        "hojas_omitidas": hojas_omitidas,
        "elecciones": len(elecciones_cargadas),
        "hechos": len(hechos),
        "localidades": len(localidades),
        "departamentos": len({l["departamento_id"] for l in localidades.values()}),
        "incidencias": len(incidencias),
    }


def _armar_sqlite() -> None:
    """Carga los CSV procesados en SQLite, con tipos e indices."""
    destino = SALIDA / "santafe_electoral.db"
    destino.unlink(missing_ok=True)
    con = sqlite3.connect(destino)
    con.executescript((RAIZ / "src" / "esquema.sql").read_text(encoding="utf-8"))

    # El orden importa: las dimensiones y fuentes van antes que los hechos,
    # porque las claves foraneas se validan al insertar.
    tablas = {
        "dim_eleccion": ("dim_eleccion.csv",
                         ["eleccion_id", "anio", "instancia", "fecha", "orden_cronologico", "cargada", "nota"]),
        "fuentes": ("fuentes.csv",
                    ["fuente_id", "archivo", "eleccion_id", "organismo", "archivo_origen",
                     "unidad_original", "recuento", "cobertura_declarada", "fecha_proceso_origen",
                     "sha256", "observaciones"]),
        "dim_departamento": ("dim_departamento.csv",
                             ["departamento_id", "departamento", "codigo_dine", "distrito_id",
                              "distrito", "anio_nomenclador"]),
        "dim_color_agrupacion": ("dim_color_agrupacion.csv",
                                 ["anio", "agrupacion_id_dine", "agrupacion_key", "nombre_fuente",
                                  "color", "distrito_id"]),
        "control_totales": ("control_totales.csv",
                            ["eleccion_id", "ambito", "distrito", "tipo_voto", "agrupacion_key",
                             "nombre_fuente", "formula", "votos", "fuente_id"]),
        "control_padron": ("control_padron.csv",
                           ["eleccion_id", "ambito", "distrito", "electores", "mesas", "votantes",
                            "fuente_id"]),
        "dim_localidad": ("dim_localidad.csv",
                          ["localidad_id", "localidad", "departamento_id", "departamento"]),
        "dim_circuito": ("dim_circuito.csv",
                         ["circuito_id", "eleccion_id", "departamento_id", "departamento",
                          "localidad_id", "localidad", "fuente_id"]),
        "dim_agrupacion": ("dim_agrupacion.csv",
                           ["agrupacion_key", "eleccion_id", "nombre_fuente", "formula",
                            "etiqueta_tipo", "espacio_politico"]),
        "padron": ("padron.csv",
                   ["eleccion_id", "departamento_id", "localidad_id", "mesas", "electores", "fuente_id"]),
        "hechos_votos": ("santafe_presidenciales_2003_2023.csv", CAMPOS_HECHOS),
        "incidencias": ("incidencias.csv",
                        ["eleccion_id", "localidad_id", "control", "esperado", "obtenido", "diferencia"]),
    }
    for tabla, (archivo, campos) in tablas.items():
        ruta = SALIDA / archivo
        if not ruta.exists():
            continue
        with open(ruta, newline="", encoding="utf-8") as fh:
            filas = [tuple(f[k] if f[k] != "" else None for k in campos) for f in csv.DictReader(fh)]
        if filas:
            marcas = ",".join("?" * len(campos))
            try:
                con.executemany(f"INSERT INTO {tabla} ({','.join(campos)}) VALUES ({marcas})", filas)
            except sqlite3.Error as err:
                raise RuntimeError(f"Fallo al cargar la tabla {tabla}: {err}") from err
    con.commit()
    con.close()


if __name__ == "__main__":
    resumen = construir()
    if resumen["archivos"] == 0 and resumen["archivos_control"] == 0:
        print("No hay archivos en data/raw/. Ver docs/03-pendientes.md.")
        sys.exit(1)
    print(
        f"Serie: {resumen['hechos']} filas de hechos | "
        f"{resumen['elecciones']}/12 instancias | "
        f"{resumen['departamentos']} de {resumen['departamentos_nomenclador']} departamentos | "
        f"{resumen['localidades']} localidades | "
        f"{resumen['incidencias']} incidencia(s)"
    )
    print(f"Control: {resumen['control_filas']} filas desde "
          f"{resumen['archivos_control']} planilla(s) por distrito")
    print(f"Colores oficiales: {resumen['colores']} agrupaciones de Santa Fe")
    for hoja in resumen["hojas_omitidas"]:
        print(f"  Hoja omitida: {hoja['hoja']} ({hoja['archivo']}) - {hoja['motivo']}")
