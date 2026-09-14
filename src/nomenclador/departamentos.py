"""Nomenclador oficial de departamentos de Santa Fe.

Fuente: AmbitosElectorales_<anio>_<instancia>.csv de la DINE, que publica los
distritos y secciones electorales. En Santa Fe la 'seccion' es el departamento
y su id es el codigo oficial, de 1 (La Capital) a 19 (San Lorenzo).

Tener este codigo importa por dos razones: da una clave estable que no depende
de como se escriba el nombre, y es la que permite unir con las capas
geograficas para los mapas.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import comunes as c  # noqa: E402

DISTRITO_SANTA_FE = "21"


def leer(ruta: Path, distrito: str = DISTRITO_SANTA_FE) -> list[dict]:
    """Devuelve los departamentos del distrito, con su codigo oficial."""
    salida = []
    with open(ruta, newline="", encoding="utf-8-sig") as fh:
        for fila in csv.DictReader(fh):
            if fila["distrito_id"].strip() != distrito:
                continue
            nombre = c.normalizar_nombre(fila["seccion_nombre"])
            salida.append({
                "departamento_id": c.clave(nombre),
                "departamento": nombre,
                "codigo_dine": int(fila["seccion_id"]),
                "distrito_id": int(fila["distrito_id"]),
                "distrito": c.normalizar_nombre(fila["distrito_nombre"]),
                "anio_nomenclador": int(fila["año"]),
            })
    salida.sort(key=lambda d: d["codigo_dine"])
    return salida


if __name__ == "__main__":
    for d in leer(Path(sys.argv[1])):
        print(f"{d['codigo_dine']:>3}  {d['departamento_id']:<20} {d['departamento']}")
