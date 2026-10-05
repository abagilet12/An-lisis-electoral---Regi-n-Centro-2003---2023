"""Genera planillas de control con los dos layouts problematicos de la DINE.

1. Layout 2011-PASO: intercala una fila 'VOTOS VÁLIDOS' entre las agrupaciones y
   el resto del pie. Si se la toma por una agrupacion, los votos se duplican.
2. Layout con una etiqueta de total desconocida, que el ingestor debe rechazar
   en vez de cargarla como si fuera un partido.
"""

from pathlib import Path

import openpyxl

DIR = Path(__file__).parent


def _encabezado(ws, titulo, fecha_texto, electores):
    ws.append([titulo])
    ws.append([f"PRESIDENTE Y VICEPRESIDENTE - {fecha_texto}"])
    ws.append([])
    ws.append(["ELECTORES INSCRIPTOS", electores])
    ws.append(["PORCENTAJE DE VOTANTES", 0.7558])
    ws.append([])
    ws.append(["FÓRMULAS", "AGRUPACIONES POLÍTICAS", "VOTOS", "% VÁLIDOS"])


def con_subtotal() -> Path:
    """Réplica reducida del layout 2011-PASO, con la fila 'VOTOS VÁLIDOS'."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Santa Fe"
    _encabezado(ws, "SANTA FE", "ELECCIONES PRIMARIAS - 14 DE AGOSTO DE 2011", 2440284)
    ws.append(["FERNÁNDEZ DE KIRCHNER - BOUDOU", "Alianza Frente para la Victoria", 676812, 37.24])
    ws.append(["BINNER - MORANDINI", "Alianza Frente Amplio Progresista", 585682, 32.23])
    ws.append([None, "VOTOS VÁLIDOS", 1293188, 98.53])   # 676812 + 585682 + 30694
    ws.append([None, "VOTOS POSITIVOS", 1262494, 96.82])
    ws.append([None, "VOTOS EN BLANCO", 30694, 1.72])
    ws.append([None, "VOTOS NULOS", 27035, 1.47])
    ws.append([None, "TOTAL DE VOTANTES", 1320223])
    destino = DIR / "control_con_subtotal.xlsx"
    wb.save(destino)
    return destino


def con_etiqueta_desconocida() -> Path:
    """Igual que el anterior pero con un total que el vocabulario no contempla."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Santa Fe"
    _encabezado(ws, "SANTA FE", "ELECCIONES PRIMARIAS - 14 DE AGOSTO DE 2011", 2440284)
    ws.append(["FERNÁNDEZ DE KIRCHNER - BOUDOU", "Alianza Frente para la Victoria", 676812, 37.24])
    ws.append([None, "VOTOS DE ULTRAMAR", 1234, 0.1])
    ws.append([None, "VOTOS POSITIVOS", 676812, 96.82])
    ws.append([None, "TOTAL DE VOTANTES", 676812])
    destino = DIR / "control_etiqueta_desconocida.xlsx"
    wb.save(destino)
    return destino


if __name__ == "__main__":
    print(con_subtotal(), con_etiqueta_desconocida(), sep="\n")
