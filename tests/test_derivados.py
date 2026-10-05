"""Prueba del ingestor de archivos derivados contra un libro de estructura real."""

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "tests" / "fixtures"))

from generar_fixture import construir  # noqa: E402
from ingest.derivados_xlsx import leer_libro  # noqa: E402

fallas = []


def chequear(condicion, mensaje):
    if not condicion:
        fallas.append(mensaje)


ruta = construir()
ing = leer_libro(ruta)

# --- Identificacion de la eleccion y de la fuente -------------------------
chequear(ing.fuente["eleccion_id"] == "2015-BALLOTAGE", "eleccion_id mal deducido")
chequear(ing.fuente["organismo"].startswith("Dirección Nacional"), "no leyo el organismo de Metodologia")
chequear(len(ing.fuente["sha256"]) == 64, "sha256 mal calculado")

# --- Positivos: uno por agrupacion, sin duplicar el total -----------------
positivos = [h for h in ing.hechos if h["tipo_voto"] == "POSITIVO"]
chequear(len(positivos) == 6, f"se esperaban 6 filas POSITIVO y hay {len(positivos)}")
chequear(all(h["agrupacion_key"] for h in positivos), "hay positivos sin agrupacion_key")
ataliva = [h for h in positivos if h["localidad_id"] == "ATALIVA"]
chequear(sum(h["votos"] for h in ataliva) == 1294, "los positivos de Ataliva no suman 1294")

# 2015 publica agrupaciones, no formulas: la columna formula queda vacia.
chequear(all(h["formula"] is None for h in positivos), "2015 no deberia completar 'formula'")

# --- No positivos: sin agrupacion y sin la columna POSITIVO ---------------
no_positivos = [h for h in ing.hechos if h["tipo_voto"] != "POSITIVO"]
chequear({h["tipo_voto"] for h in no_positivos} == {"BLANCO", "NULO", "RECURRIDO", "IMPUGNADO"},
         "vocabulario de tipo_voto inesperado")
chequear(all(h["agrupacion_key"] is None for h in no_positivos), "un no positivo trae agrupacion")
blanco_ataliva = [h for h in no_positivos if h["localidad_id"] == "ATALIVA" and h["tipo_voto"] == "BLANCO"]
chequear(blanco_ataliva and blanco_ataliva[0]["votos"] == 23, "'EN BLANCO' no se mapeo a BLANCO=23")

# --- Claves normalizadas --------------------------------------------------
chequear(any(h["localidad_id"] == "ZENON_PEREYRA" for h in ing.hechos), "clave de localidad sin normalizar")
chequear(all(h["departamento_id"] == "CASTELLANOS" for h in ing.hechos), "clave de departamento mal formada")

# --- Padron y nomenclador -------------------------------------------------
chequear(len(ing.padron) == 3, "padron incompleto")
chequear(ing.padron[0]["electores"] == 1671, "electores mal leidos")
chequear({c["circuito_id"] for c in ing.circuitos} == {"0121", "0120", "0138"}, "nomenclador mal leido")

# --- El descuadre deliberado tiene que aparecer como incidencia -----------
chequear(len(ing.incidencias) == 1, f"se esperaba 1 incidencia y hay {len(ing.incidencias)}")
if ing.incidencias:
    inc = ing.incidencias[0]
    chequear(inc["localidad_id"] == "ZENON_PEREYRA" and inc["diferencia"] == -3,
             f"incidencia mal calculada: {inc}")

if fallas:
    print("FALLAS:")
    for f in fallas:
        print(" -", f)
    sys.exit(1)
print(f"OK - {len(ing.hechos)} hechos, {len(ing.padron)} filas de padron, "
      f"{len(ing.circuitos)} circuitos, {len(ing.incidencias)} incidencia(s)")
