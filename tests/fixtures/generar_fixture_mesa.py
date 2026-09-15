"""Genera un archivo a nivel mesa con las trampas del formato real de la DINE.

Incluye a proposito: filas de otro distrito y de otro cargo (que hay que
descartar), dos listas internas de una misma agrupacion en PASO (que hay que
sumar sin duplicar), el padron repetido en cada fila de una misma mesa (que hay
que contar una sola vez) y un circuito ausente del nomenclador (que no se puede
perder).
"""

import csv
from pathlib import Path

DESTINO = Path(__file__).parent / "mesa_paso_2023.csv"

COLUMNAS = ["año", "eleccion_tipo", "recuento_tipo", "padron_tipo", "distrito_id",
            "distrito_nombre", "seccionprovincial_id", "seccion_id", "seccion_nombre",
            "circuito_id", "circuito_nombre", "mesa_id", "mesa_tipo", "mesa_electores",
            "cargo_id", "cargo_nombre", "agrupacion_id", "agrupacion_nombre",
            "lista_numero", "lista_nombre", "votos_tipo", "votos_cantidad"]


def _fila(seccion_id, seccion, circuito, mesa, electores, agrupacion_id, agrupacion,
          lista, votos_tipo, votos, distrito="21", distrito_nombre="Santa Fe",
          cargo="PRESIDENTE/A"):
    return {
        "año": "2023", "eleccion_tipo": "PASO", "recuento_tipo": "PROVISORIO",
        "padron_tipo": "NORMAL", "distrito_id": distrito, "distrito_nombre": distrito_nombre,
        "seccionprovincial_id": "0", "seccion_id": seccion_id, "seccion_nombre": seccion,
        "circuito_id": circuito, "circuito_nombre": circuito, "mesa_id": mesa,
        "mesa_tipo": "NATIVOS", "mesa_electores": electores, "cargo_id": "1",
        "cargo_nombre": cargo, "agrupacion_id": agrupacion_id, "agrupacion_nombre": agrupacion,
        "lista_numero": lista, "lista_nombre": f"LISTA {lista}", "votos_tipo": votos_tipo,
        "votos_cantidad": votos,
    }


def construir() -> Path:
    filas = []

    # Mesa 1, circuito 0055 (Esperanza, en el nomenclador). Padrón 350.
    # La agrupación 134 presenta dos listas internas: 100 + 40 = 140.
    filas += [
        _fila("2", "Las Colonias", "0055", "1", 350, "134", "UNION POR LA PATRIA", "1A", "POSITIVO", 100),
        _fila("2", "Las Colonias", "0055", "1", 350, "134", "UNION POR LA PATRIA", "2B", "POSITIVO", 40),
        _fila("2", "Las Colonias", "0055", "1", 350, "135", "LA LIBERTAD AVANZA", "3C", "POSITIVO", 120),
        _fila("2", "Las Colonias", "0055", "1", 350, "", "", "", "EN BLANCO", 8),
        _fila("2", "Las Colonias", "0055", "1", 350, "", "", "", "NULO", 2),
    ]
    # Mesa 2, mismo circuito. Padrón 300: el total de Esperanza debe dar 650, no más.
    filas += [
        _fila("2", "Las Colonias", "0055", "2", 300, "134", "UNION POR LA PATRIA", "1A", "POSITIVO", 90),
        _fila("2", "Las Colonias", "0055", "2", 300, "135", "LA LIBERTAD AVANZA", "3C", "POSITIVO", 110),
    ]
    # Mesa 3, circuito 0999: NO está en el nomenclador, pero es de Las Colonias.
    # Sus votos no se pueden perder ni salir del departamento.
    filas += [
        _fila("2", "Las Colonias", "0999", "3", 200, "135", "LA LIBERTAD AVANZA", "3C", "POSITIVO", 150),
        _fila("2", "Las Colonias", "0999", "3", 200, "", "", "", "NULO", 5),
    ]
    # Mesa 4, otro departamento: la cobertura departamental sale sin nomenclador.
    filas += [
        _fila("13", "Rosario", "0500", "4", 400, "134", "UNION POR LA PATRIA", "1A", "POSITIVO", 210),
    ]
    # Ruido que hay que descartar: otro distrito y otro cargo.
    filas += [
        _fila("1", "La Plata", "1000", "9", 999, "134", "UNION POR LA PATRIA", "1A", "POSITIVO", 9999,
              distrito="2", distrito_nombre="Buenos Aires"),
        _fila("2", "Las Colonias", "0055", "1", 350, "134", "UNION POR LA PATRIA", "1A", "POSITIVO", 7777,
              cargo="DIPUTADO/A NACIONAL"),
    ]

    with open(DESTINO, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNAS)
        w.writeheader()
        w.writerows(filas)
    return DESTINO


if __name__ == "__main__":
    print(construir())
