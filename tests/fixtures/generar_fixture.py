"""Genera un libro de prueba con la misma estructura que los archivos reales.

Los valores son un subconjunto textual del 'Votos por Localidad - Ballotage 2015'
real (departamento Castellanos), mas una localidad inventada con un descuadre
deliberado para ejercitar el control de positivos.
"""

from pathlib import Path

import openpyxl

DESTINO = Path(__file__).parent / "Votos por Localidad - Ballotage 2015 - Presidente - Santa Fe.xlsx"


def construir() -> Path:
    wb = openpyxl.Workbook()

    ws = wb.active
    ws.title = "Votos por Localidad"
    ws.append(["Departamento", "Localidad", "Agrupacion_Politica", "Votos"])
    for fila in [
        ("Castellanos", "Ataliva", "CAMBIEMOS", 935),
        ("Castellanos", "Ataliva", "FRENTE PARA LA VICTORIA", 359),
        ("Castellanos", "Colonia Aldao", "CAMBIEMOS", 796),
        ("Castellanos", "Colonia Aldao", "FRENTE PARA LA VICTORIA", 415),
        ("Castellanos", "Zenón Pereyra", "CAMBIEMOS", 890),
        ("Castellanos", "Zenón Pereyra", "FRENTE PARA LA VICTORIA", 322),
    ]:
        ws.append(fila)

    # Hoja derivada que el pipeline debe ignorar.
    ws = wb.create_sheet("Agrupacion Ganadora por Local")
    ws.append(["Departamento", "Localidad", "Agrupacion_Ganadora", "Votos_Ganador",
               "Mesas", "Electores", "Porcentaje_sobre_Electores"])
    ws.append(["Castellanos", "Ataliva", "CAMBIEMOS", 935, 5, 1671, 55.95])

    # Orden de columnas distinto al de 2007 a proposito: se lee por nombre.
    ws = wb.create_sheet("Totales por Tipo de Voto")
    ws.append(["Departamento", "Localidad", "EN BLANCO", "IMPUGNADO", "NULO", "POSITIVO", "RECURRIDO"])
    ws.append(["Castellanos", "Ataliva", 23, 0, 6, 1294, 0])
    ws.append(["Castellanos", "Colonia Aldao", 7, 0, 11, 1211, 0])
    # Descuadre deliberado: declara 1215 y las agrupaciones suman 1212.
    ws.append(["Castellanos", "Zenón Pereyra", 10, 0, 5, 1215, 0])

    ws = wb.create_sheet("Electores y Mesas")
    ws.append(["Departamento", "Localidad", "Mesas", "Electores"])
    ws.append(["Castellanos", "Ataliva", 5, 1671])
    ws.append(["Castellanos", "Colonia Aldao", 5, 1571])
    ws.append(["Castellanos", "Zenón Pereyra", 5, 1466])

    ws = wb.create_sheet("Nomenclador Circuito-Localidad")
    ws.append(["Circuito", "Departamento", "Localidad"])
    ws.append(["0121", "Castellanos", "Ataliva"])
    ws.append(["0120", "Castellanos", "Colonia Aldao"])
    ws.append(["0138", "Castellanos", "Zenón Pereyra"])

    ws = wb.create_sheet("Metodologia")
    ws.append(["Concepto", "Descripcion"])
    ws.append(["Archivo fuente requerido", "presentacionDeResultadosBallotage_SantaFe_2015.csv"])
    ws.append(["Organismo de origen", "Dirección Nacional Electoral (DINE), Ministerio del Interior."])
    ws.append(["Unidad original del archivo fuente", "Mesa electoral."])
    ws.append(["Departamentos cubiertos", "Castellanos, Las Colonias, San Martín"])
    ws.append(["Fecha de procesamiento", "2026-06-25 15:48"])

    wb.save(DESTINO)
    return DESTINO


if __name__ == "__main__":
    print(construir())
