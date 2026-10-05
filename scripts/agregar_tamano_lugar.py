#!/usr/bin/env python3
"""
Inserta en el tablero los datos de «El voto según el tamaño del lugar».

Toma salida/datos_tamano_lugar.json (lo genera scripts/construir_tamano_lugar.py) y lo escribe
entre las marcas /*TAMANO-DATOS:INI*/ y /*TAMANO-DATOS:FIN*/ de salida/voto_santafesino.html.
Se puede correr las veces que haga falta.

Uso: python3 scripts/agregar_tamano_lugar.py [html] [datos_tamano_lugar.json]
"""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
HTML = Path(sys.argv[1]) if len(sys.argv) > 1 else RAIZ / "salida" / "voto_santafesino.html"
DATOS = Path(sys.argv[2]) if len(sys.argv) > 2 else RAIZ / "salida" / "datos_tamano_lugar.json"

s = HTML.read_text(encoding="utf-8")
ini, fin = "/*TAMANO-DATOS:INI*/", "/*TAMANO-DATOS:FIN*/"
assert ini in s and fin in s, "faltan las marcas TAMANO-DATOS en el HTML"
a = s.index(ini) + len(ini); b = s.index(fin)
s = s[:a] + "\nconst T = " + DATOS.read_text(encoding="utf-8") + ";\n" + s[b:]
HTML.write_text(s, encoding="utf-8")
print(f"{HTML} · {len(s)/1024/1024:.2f} MB")
