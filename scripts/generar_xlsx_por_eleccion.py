#!/usr/bin/env python3
"""
Genera un .xlsx por eleccion en salida/xlsx/, segun docs/CRITERIO_BASE_DE_DATOS.md.

Cada archivo se arma al nivel mas fino disponible para esa eleccion
(circuito > localidad > provincia) y trae cinco hojas:

  Resumen            una fila: totales y participacion de la eleccion
  Resultados_ancho   una fila por unidad, una columna por agrupacion
  Resultados_largo   una fila por unidad x agrupacion (tidy, para pandas)
  Nomenclador        una fila por unidad, para cruzar con cartografia
  Metadatos          procedencia, controles y advertencias

Las hojas de datos empiezan con los encabezados en la fila 1, sin celdas
combinadas: pd.read_excel() las lee sin argumentos extra. Los valores
derivados (participacion, totales, porcentajes) son formulas.
"""
import csv
import sys
from collections import defaultdict
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

RAIZ = Path(__file__).resolve().parent.parent
PROC = RAIZ / "datos" / "procesados"
SALIDA = RAIZ / "salida" / "xlsx"

FUENTE = "Arial"
ENCABEZADO_FILL = PatternFill("solid", fgColor="1F3864")
ENCABEZADO_FONT = Font(name=FUENTE, bold=True, color="FFFFFF", size=10)
NORMAL = Font(name=FUENTE, size=10)
TITULO = Font(name=FUENTE, bold=True, size=10)

CARGO = "PRESIDENTE Y VICE"
DISTRITO_ID, DISTRITO = "21", "Santa Fe"

NO_POSITIVOS = ["blancos", "nulos", "impugnados", "recurridos", "comando"]

FECHAS = {
    ("2003", "GENERAL"): "2003-04-27", ("2007", "GENERAL"): "2007-10-28",
    ("2011", "PASO"): "2011-08-14", ("2011", "GENERAL"): "2011-10-23",
    ("2015", "PASO"): "2015-08-09", ("2015", "GENERAL"): "2015-10-25",
    ("2015", "BALOTAJE"): "2015-11-22",
    ("2019", "PASO"): "2019-08-11", ("2019", "GENERAL"): "2019-10-27",
    ("2023", "PASO"): "2023-08-13", ("2023", "GENERAL"): "2023-10-22",
    ("2023", "BALOTAJE"): "2023-11-19",
}
ORDEN = {"PASO": 0, "GENERAL": 1, "BALOTAJE": 2}


def leer(nombre):
    ruta = PROC / nombre
    if not ruta.exists():
        return []
    return list(csv.DictReader(open(ruta, encoding="utf-8")))


def entero(v):
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return 0


# --------------------------------------------------------------------------
# Carga: para cada eleccion se arma la unidad de analisis mas fina disponible.
# --------------------------------------------------------------------------

def cargar():
    """Devuelve {(anio, instancia): dict con unidades, votos y procedencia}."""
    elecciones = {}

    # --- Nivel circuito (el mas fino) -------------------------------------
    nomencladores = {}
    for ruta in sorted(PROC.glob("nomenclador_circuitos_*.csv")):
        for r in csv.DictReader(open(ruta, encoding="utf-8")):
            nomencladores.setdefault(r["anio_referencia"], {})[r["circuito_id"]] = r

    # Un archivo puede traer una eleccion (los agregados desde mesa) o varias
    # (el consolidado de PolAr), asi que siempre se agrupa por eleccion.
    circuito = ["resultados_circuito_polar.csv"] + [
        p.name for p in sorted(PROC.glob("*_circuito.csv"))]
    for nombre in circuito:
        ruta = PROC / nombre
        if not ruta.exists():
            continue
        por_eleccion_circ = defaultdict(list)
        for r in csv.DictReader(open(ruta, encoding="utf-8")):
            por_eleccion_circ[(r["anio"], r["instancia"])].append(r)
        for clave, filas in por_eleccion_circ.items():
            if clave in elecciones:        # ya cargada de otro archivo
                continue
            elecciones[clave] = {
                "nivel": "circuito", "clave": "circuito_id", "filas": filas,
                "nomenclador": nomencladores.get(clave[0], {}),
                "recuento": filas[0].get("recuento_tipo", "NO DECLARADO"),
                "fuente": filas[0].get("fuente")
                          or filas[0].get("archivo_origen", ""),
            }

    # --- Nivel localidad ---------------------------------------------------
    por_eleccion = defaultdict(list)
    for r in leer("serie_localidad.csv"):
        por_eleccion[(r["anio"], r["instancia"])].append(r)

    meta_loc = {}
    for nombre in ["metadatos_localidad.csv"] + [
        p.name for p in sorted(PROC.glob("*_localidad_desde_mesa_metadatos.csv"))
    ]:
        for r in leer(nombre):
            meta_loc[(r["anio"], r["instancia"], r["seccion"], r["localidad"])] = r

    for clave, filas in por_eleccion.items():
        if clave in elecciones:   # ya hay circuito, que es mas fino
            continue
        elecciones[clave] = {
            "nivel": "localidad", "clave": "localidad", "filas": filas,
            "nomenclador": {}, "metadatos_unidad": meta_loc,
            "recuento": filas[0].get("recuento_tipo") or "NO DECLARADO",
            "fuente": filas[0].get("fuente", ""),
        }

    # --- Nivel provincial ---------------------------------------------------
    provinciales = [
        ("resultados.csv", "Consulta de Escrutinio por Zona (JNE)", "DEFINITIVO"),
        ("resultados_provincia_dine.csv", "Resultados DINE", "NO DECLARADO"),
        ("resultados_provincia_transcripto.csv", "Transcripción manual",
         "DEFINITIVO"),
    ]
    for nombre, etiqueta, recuento in provinciales:
        agrupado = defaultdict(list)
        for r in leer(nombre):
            agrupado[(r["anio"], r["instancia"])].append(r)
        for clave, filas in agrupado.items():
            if clave in elecciones:
                continue
            elecciones[clave] = {
                "nivel": "provincia", "clave": "distrito", "filas": filas,
                "nomenclador": {},
                "recuento": filas[0].get("recuento_tipo") or recuento,
                "fuente": etiqueta,
            }
    return elecciones


def organizar(datos):
    """Reduce las filas crudas a: unidades, agrupaciones y votos por celda."""
    nivel, filas = datos["nivel"], datos["filas"]
    votos = defaultdict(int)          # (unidad, etiqueta) -> votos
    unidades, agrupaciones = {}, {}

    for r in filas:
        tipo = r["tipo_registro"]
        if tipo in ("lista", "formula", "positivo", "validos", "total",
                    "inscriptos", "participacion"):
            continue
        if nivel == "circuito":
            uid = r["circuito_id"]
            unidades.setdefault(uid, {
                "circuito_id": uid, "seccion_id": r.get("seccion_id", ""),
                "seccion": r.get("seccion", ""),
                "localidad": r.get("localidad", ""),
            })
        elif nivel == "localidad":
            uid = (r["seccion"], r["localidad"])
            unidades.setdefault(uid, {
                "circuito_id": r.get("circuito_id", ""),
                "seccion_id": "", "seccion": r["seccion"],
                "localidad": r["localidad"],
            })
        else:
            uid = DISTRITO
            unidades.setdefault(uid, {"circuito_id": "", "seccion_id": "",
                                      "seccion": "", "localidad": ""})

        etiqueta = r["agrupacion"] if tipo == "agrupacion" else tipo
        if tipo == "agrupacion":
            agrupaciones[etiqueta] = agrupaciones.get(etiqueta, 0) + entero(r["votos"])
        votos[(uid, etiqueta)] += entero(r["votos"])

    orden_agrup = [a for a, _ in sorted(agrupaciones.items(),
                                        key=lambda kv: -kv[1])]
    return unidades, orden_agrup, votos


def padron_de(datos, uid, unidad):
    """Padron y mesas de la unidad, si la fuente los trae."""
    if datos["nivel"] == "circuito":
        n = datos["nomenclador"].get(unidad["circuito_id"])
        if n:
            return entero(n["electores"]), entero(n["mesas"])
        # PolAr trae padron y mesas en cada fila, sin nomenclador aparte.
        for f in datos["filas"]:
            if f.get("circuito_id") == unidad["circuito_id"] and f.get("electores"):
                return entero(f["electores"]), entero(f.get("mesas", 0))
    elif datos["nivel"] == "localidad":
        filas = datos["filas"]
        m = datos.get("metadatos_unidad", {}).get(
            (filas[0]["anio"], filas[0]["instancia"], *uid))
        if m:
            return entero(m["electores"]), entero(m["mesas"])
    else:
        for r in datos["filas"]:
            if r["tipo_registro"] == "inscriptos":
                return entero(r["votos"]), 0
    return 0, 0


# --------------------------------------------------------------------------
# Escritura
# --------------------------------------------------------------------------

def encabezar(ws, columnas, anchos=None):
    ws.append(columnas)
    for i, _ in enumerate(columnas, start=1):
        c = ws.cell(row=1, column=i)
        c.font, c.fill = ENCABEZADO_FONT, ENCABEZADO_FILL
        c.alignment = Alignment(horizontal="center", vertical="center",
                                wrap_text=True)
        ws.column_dimensions[get_column_letter(i)].width = (
            anchos[i - 1] if anchos else 14)
    ws.freeze_panes = "A2"


def escribir_eleccion(anio, instancia, datos):
    unidades, agrupaciones, votos = organizar(datos)
    nivel = datos["nivel"]
    fecha = FECHAS.get((anio, instancia), "")
    wb = Workbook()

    # ---------------- Resultados_ancho ------------------------------------
    ws = wb.active
    ws.title = "Resultados_ancho"
    cols = (["anio", "instancia", "fecha", "cargo", "distrito_id", "distrito",
             "seccion_id", "seccion", "circuito_id", "localidad",
             "electores", "mesas"]
            + [a.lower().replace(" ", "_")[:60] for a in agrupaciones]
            + NO_POSITIVOS + ["positivos", "total_votantes", "participacion"])
    encabezar(ws, cols, [8, 10, 11, 18, 10, 12, 10, 18, 12, 22]
              + [12, 8] + [16] * len(agrupaciones) + [11] * 8)

    col_agrup_ini = 13
    col_agrup_fin = col_agrup_ini + len(agrupaciones) - 1
    col_nopos_ini = col_agrup_fin + 1
    col_nopos_fin = col_nopos_ini + len(NO_POSITIVOS) - 1
    col_pos = col_nopos_fin + 1
    col_tot, col_part = col_pos + 1, col_pos + 2
    col_electores = 11

    for fila, (uid, u) in enumerate(sorted(
            unidades.items(),
            key=lambda kv: (kv[1]["seccion"], kv[1]["localidad"],
                            kv[1]["circuito_id"])), start=2):
        electores, mesas = padron_de(datos, uid, u)
        v_agrup = [votos.get((uid, a), 0) for a in agrupaciones]
        v_nopos = [votos.get((uid, t), 0) for t in NO_POSITIVOS]
        positivos = sum(v_agrup)
        total = positivos + sum(v_nopos)
        # Valores calculados, no formulas: ver nota en Metadatos.
        participacion = (total / electores) if electores else None
        ws.append([anio, instancia, fecha, CARGO, DISTRITO_ID, DISTRITO,
                   u["seccion_id"], u["seccion"], u["circuito_id"],
                   u["localidad"], electores or None, mesas or None]
                  + v_agrup + v_nopos + [positivos, total, participacion])
        ws.cell(row=fila, column=col_part).number_format = "0.00%"

    for f in ws.iter_rows(min_row=2):
        for c in f:
            c.font = NORMAL
            if c.column >= col_electores and c.column != col_part:
                c.number_format = "#,##0"
    for c in ("E", "G", "I"):                    # ids: texto, conservan ceros
        for celda in ws[c][1:]:
            celda.number_format = "@"

    # ---------------- Resultados_largo ------------------------------------
    wl = wb.create_sheet("Resultados_largo")
    encabezar(wl, ["anio", "instancia", "fecha", "cargo", "distrito_id",
                   "distrito", "seccion_id", "seccion", "circuito_id",
                   "localidad", "agrupacion", "tipo_registro", "votos"],
              [8, 10, 11, 18, 10, 12, 10, 18, 12, 22, 40, 14, 12])
    for uid, u in sorted(unidades.items(),
                         key=lambda kv: (kv[1]["seccion"], kv[1]["localidad"],
                                         kv[1]["circuito_id"])):
        for etiqueta in agrupaciones + NO_POSITIVOS:
            tipo = "agrupacion" if etiqueta in agrupaciones else etiqueta
            wl.append([anio, instancia, fecha, CARGO, DISTRITO_ID, DISTRITO,
                       u["seccion_id"], u["seccion"], u["circuito_id"],
                       u["localidad"], etiqueta, tipo,
                       votos.get((uid, etiqueta), 0)])
    for f in wl.iter_rows(min_row=2):
        for c in f:
            c.font = NORMAL
        f[12].number_format = "#,##0"

    # ---------------- Resumen ---------------------------------------------
    wr = wb.create_sheet("Resumen", 0)
    n = len(unidades) + 1
    wr.append(["Elección", f"{instancia} {anio} · {CARGO} · {DISTRITO}"])
    wr.append(["Fecha", fecha])
    wr.append(["Nivel de agregación", nivel])
    wr.append(["Unidades", len(unidades)])
    wr.append([])
    encabezado_fila = wr.max_row + 1
    wr.append(["concepto", "votos", "porcentaje"])
    totales = {a: sum(votos.get((uid, a), 0) for uid in unidades)
               for a in agrupaciones + NO_POSITIVOS}
    positivos = sum(totales[a] for a in agrupaciones)
    total_votantes = positivos + sum(totales[t] for t in NO_POSITIVOS)
    padron = sum(padron_de(datos, uid, u)[0] for uid, u in unidades.items())

    for i, nombre in enumerate(agrupaciones + NO_POSITIVOS):
        f = encabezado_fila + 1 + i
        wr.append([nombre, totales[nombre],
                   totales[nombre] / positivos if positivos else None])
        wr.cell(row=f, column=2).number_format = "#,##0"
        wr.cell(row=f, column=3).number_format = "0.00%"
    fila_pos = wr.max_row + 1
    for nombre, valor in (("VOTOS POSITIVOS", positivos),
                          ("TOTAL VOTANTES", total_votantes),
                          ("ELECTORES INSCRIPTOS", padron)):
        wr.append([nombre, valor, None])
        wr.cell(row=wr.max_row, column=2).number_format = "#,##0"
    wr.append(["PARTICIPACIÓN",
               total_votantes / padron if padron else None, None])
    wr.cell(row=wr.max_row, column=2).number_format = "0.00%"
    for f in wr.iter_rows():
        for c in f:
            c.font = NORMAL
    for f in (1, 2, 3, 4, encabezado_fila):
        for c in wr[f]:
            c.font = TITULO
    for col, ancho in (("A", 34), ("B", 18), ("C", 14)):
        wr.column_dimensions[col].width = ancho

    # ---------------- Nomenclador -----------------------------------------
    wn = wb.create_sheet("Nomenclador")
    encabezar(wn, ["circuito_id", "seccion_id", "seccion", "localidad",
                   "mesas", "electores", "anio"], [12, 10, 20, 24, 9, 12, 8])
    for uid, u in sorted(unidades.items(),
                         key=lambda kv: (kv[1]["seccion"], kv[1]["localidad"],
                                         kv[1]["circuito_id"])):
        electores, mesas = padron_de(datos, uid, u)
        wn.append([u["circuito_id"], u["seccion_id"], u["seccion"],
                   u["localidad"], mesas or None, electores or None, anio])
    for f in wn.iter_rows(min_row=2):
        for c in f:
            c.font = NORMAL
        f[0].number_format = f[1].number_format = "@"

    # ---------------- Metadatos -------------------------------------------
    wm = wb.create_sheet("Metadatos")
    encabezar(wm, ["clave", "valor"], [30, 110])
    advertencia = (
        "El recuento provisorio NO es el escrutinio definitivo: difiere "
        "alrededor de 2% en las fuerzas principales. Ver "
        "docs/NOTA_METODOLOGICA_2023.md."
        if datos["recuento"] == "PROVISORIO" else
        "El recuento no está declarado en la fuente; verificar antes de citar."
        if datos["recuento"] == "NO DECLARADO" else
        "Escrutinio definitivo.")
    for clave, valor in [
        ("anio", anio), ("instancia", instancia), ("fecha", fecha),
        ("cargo", CARGO), ("distrito", f"{DISTRITO} (id {DISTRITO_ID})"),
        ("nivel_agregacion", nivel),
        ("unidades", len(unidades)),
        ("agrupaciones", len(agrupaciones)),
        ("recuento_tipo", datos["recuento"]),
        ("fuente", datos["fuente"]),
        ("advertencia", advertencia),
        ("criterio", "docs/CRITERIO_BASE_DE_DATOS.md"),
        ("nota_valores_calculados",
         "Las columnas derivadas (positivos, total_votantes, participacion) "
         "son valores, no fórmulas: una fórmula escrita por openpyxl no lleva "
         "valor cacheado y pandas la leería vacía. El script es la fuente de "
         "verdad: para rehacerlas, correr "
         "scripts/generar_xlsx_por_eleccion.py, no editar el archivo."),
        ("control_agrupaciones_vs_positivos",
         "Verificado por el parser en cada corrida."),
        ("nota_circuito_id",
         "Texto con ceros a la izquierda. Los códigos cambian entre años: "
         "Santa Fe renumeró sus circuitos en 2023."),
        ("nota_suma",
         "Al sumar votos, filtrar tipo_registro == 'agrupacion'. Las listas "
         "internas ya están contenidas en su agrupación."),
    ]:
        wm.append([clave, str(valor)])
    for f in wm.iter_rows(min_row=2):
        for c in f:
            c.font, c.alignment = NORMAL, Alignment(wrap_text=True,
                                                    vertical="top")

    SALIDA.mkdir(parents=True, exist_ok=True)
    destino = SALIDA / f"{anio}_{instancia}_santa_fe_presidente.xlsx"
    wb.save(destino)
    return destino, nivel, len(unidades), len(agrupaciones)


def main():
    elecciones = cargar()
    if not elecciones:
        sys.exit("no hay datos procesados")
    print(f"{'elección':20} {'nivel':11} {'unidades':>9} {'agrup.':>7}  archivo")
    for clave in sorted(elecciones, key=lambda k: (k[0], ORDEN[k[1]])):
        destino, nivel, nu, na = escribir_eleccion(*clave, elecciones[clave])
        print(f"  {clave[0]} {clave[1]:12} {nivel:11} {nu:>9} {na:>7}  "
              f"{destino.name}")
    print(f"\n{len(elecciones)} archivos en salida/xlsx/")


if __name__ == "__main__":
    main()
