"""Pruebas del ingestor de planillas DINE por distrito.

El caso central es de regresion: la hoja de 2011-PASO trae una fila
'VOTOS VÁLIDOS' que, tomada por una agrupacion, duplicaba los votos positivos
de la provincia.
"""

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "tests" / "fixtures"))

from generar_fixture_control import con_etiqueta_desconocida, con_subtotal  # noqa: E402
from ingest.control_provincial import leer_libro  # noqa: E402

fallas = []


def chequear(condicion, mensaje):
    if not condicion:
        fallas.append(mensaje)


# --- 1. La fila de subtotal no se carga como agrupacion -------------------
controles, _ = leer_libro(con_subtotal())
chequear(len(controles) == 1, "se esperaba una sola hoja de control")
ctrl = controles[0]

chequear(ctrl.fuente["eleccion_id"] == "2011-PASO",
         f"instancia mal deducida de la fecha declarada: {ctrl.fuente['eleccion_id']}")

positivos = [t for t in ctrl.totales if t["tipo_voto"] == "POSITIVO"]
chequear(len(positivos) == 2, f"se esperaban 2 agrupaciones y hay {len(positivos)}")
chequear(all("VALIDOS" not in (t["agrupacion_key"] or "") for t in positivos),
         "la fila 'VOTOS VÁLIDOS' se coló como agrupación")
chequear(sum(t["votos"] for t in positivos) == 1262494,
         f"positivos mal sumados: {sum(t['votos'] for t in positivos)} (esperado 1262494)")

# El cuadre aritmético es lo que detecta este error de forma automática.
total = sum(t["votos"] for t in ctrl.totales)
chequear(total == ctrl.padron[0]["votantes"],
         f"la hoja no cuadra: {total} contra {ctrl.padron[0]['votantes']} votantes")
chequear(ctrl.padron[0]["electores"] == 2440284, "electores mal leídos del encabezado")

# La fórmula se conserva cuando la planilla publica candidatos.
chequear(any(t["formula"] and "BOUDOU" in t["formula"] for t in positivos),
         "no se guardó la fórmula presidencial")

# --- 2. Una etiqueta de total desconocida tiene que fallar ----------------
try:
    leer_libro(con_etiqueta_desconocida())
    fallas.append("una etiqueta 'VOTOS ...' desconocida se cargó en silencio en vez de fallar")
except ValueError as err:
    chequear("ULTRAMAR" in str(err), f"el error no nombra la etiqueta problemática: {err}")

if fallas:
    print("FALLAS:")
    for f in fallas:
        print(" -", f)
    sys.exit(1)
print(f"OK - control leído: {len(positivos)} agrupaciones, cuadre exacto contra votantes")
