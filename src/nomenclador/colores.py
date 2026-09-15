"""Colores oficiales de las agrupaciones, publicados por la DINE.

Fuente: Colores_<anio>.csv. Sirve para que los mapas y gráficos usen el color
con que cada fuerza se presentó, en vez de una paleta inventada.

Dos advertencias que vienen del propio archivo:

1. **El color es por distrito, no nacional.** La misma agrupación puede tener
   distinto id y distinto color según la provincia: Unión por la Patria es
   #009CDE con id 134 en Santa Fe y #FEDD00 con id 503 en otras. Por eso se lee
   filtrando por distrito y nunca se mezcla entre provincias.
2. **Solo existe para 2023.** Para el resto de la serie hay que definir una
   paleta propia, y esa decisión va atada a la de espacios políticos estables.
"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import comunes as c  # noqa: E402

DISTRITO_SANTA_FE = "21"


def anio_de_archivo(ruta: Path) -> int:
    m = re.search(r"(20\d{2})", Path(ruta).name)
    if not m:
        raise ValueError(f"No se pudo leer el anio en {Path(ruta).name!r}")
    return int(m.group(1))


def leer(ruta: Path, distrito: str = DISTRITO_SANTA_FE) -> list[dict]:
    """Devuelve los colores del distrito pedido, uno por agrupacion."""
    anio = anio_de_archivo(ruta)
    salida: dict[str, dict] = {}
    with open(ruta, newline="", encoding="utf-8-sig") as fh:
        for fila in csv.DictReader(fh):
            if fila["distrito_id"].strip() != distrito:
                continue
            nombre = c.normalizar_nombre(fila["agrupacion_nombre"])
            agrupacion_id = fila["agrupacion_id"].strip()
            salida[agrupacion_id] = {
                "anio": anio,
                "agrupacion_id_dine": int(agrupacion_id),
                "agrupacion_key": c.clave(nombre),
                "nombre_fuente": nombre,
                "color": fila["agrupacion_color"].strip().upper(),
                "distrito_id": int(fila["distrito_id"]),
            }
    return sorted(salida.values(), key=lambda d: d["agrupacion_id_dine"])


if __name__ == "__main__":
    for fila in leer(Path(sys.argv[1])):
        print(f"{fila['agrupacion_id_dine']:>4}  {fila['color']}  {fila['nombre_fuente']}")
