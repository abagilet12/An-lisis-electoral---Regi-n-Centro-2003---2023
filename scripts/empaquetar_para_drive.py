#!/usr/bin/env python3
"""
Arma un .zip con los Excel ya ordenados en las carpetas por año de Drive.

Existe para que cargar la base en Drive sea arrastrar seis carpetas en vez de
doce archivos. Los nombres de carpeta replican los de
«Análisis electoral Santa Fe 2003-2023 — Presidente».

El .zip no se versiona: duplica los Excel y queda desactualizado en cuanto se
regeneran. Se rehace corriendo este script.
"""
import shutil
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
XLSX = RAIZ / "salida" / "xlsx"
DESTINO = RAIZ / "salida" / "Excel_por_eleccion_Santa_Fe_2003-2023.zip"

CARPETAS = {
    "2003": "2003 — General",
    "2007": "2007 — General",
    "2011": "2011 — PASO y General",
    "2015": "2015 — PASO, General y Balotaje",
    "2019": "2019 — PASO y General",
    "2023": "2023 — PASO, General y Balotaje",
}


def main():
    archivos = sorted(XLSX.glob("*.xlsx"))
    if not archivos:
        sys.exit(f"no hay .xlsx en {XLSX}; correr antes "
                 "scripts/generar_xlsx_completo.py")

    staging = RAIZ / "salida" / ".paquete"
    shutil.rmtree(staging, ignore_errors=True)

    for archivo in archivos:
        anio = archivo.name[:4]
        carpeta = CARPETAS.get(anio)
        if not carpeta:
            print(f"  ! sin carpeta definida para {anio}: {archivo.name}")
            continue
        (staging / carpeta).mkdir(parents=True, exist_ok=True)
        shutil.copy2(archivo, staging / carpeta / archivo.name)

    if DESTINO.exists():
        DESTINO.unlink()
    shutil.make_archive(str(DESTINO.with_suffix("")), "zip", staging)
    shutil.rmtree(staging, ignore_errors=True)

    mb = DESTINO.stat().st_size / 1024 / 1024
    print(f"-> salida/{DESTINO.name} ({mb:.1f} MB, {len(archivos)} archivos "
          f"en {len(CARPETAS)} carpetas)")


if __name__ == "__main__":
    main()
