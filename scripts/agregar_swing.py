#!/usr/bin/env python3
"""
Inserta en el tablero los datos de la pestaña «Swing voters».

Toma salida/datos_swing.json (lo genera scripts/construir_swing.py) y lo escribe entre las marcas
/*SWING-DATOS:INI*/ y /*SWING-DATOS:FIN*/ de salida/voto_santafesino.html. Se puede correr las veces que haga falta.

Uso: python3 scripts/agregar_swing.py [html] [datos_swing.json]
"""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
HTML = Path(sys.argv[1]) if len(sys.argv) > 1 else RAIZ / "salida" / "voto_santafesino.html"
DATOS = Path(sys.argv[2]) if len(sys.argv) > 2 else RAIZ / "salida" / "datos_swing.json"

s = HTML.read_text(encoding="utf-8")
ini, fin = "/*SWING-DATOS:INI*/", "/*SWING-DATOS:FIN*/"
assert ini in s and fin in s, "faltan las marcas SWING-DATOS en el HTML"
a = s.index(ini) + len(ini); b = s.index(fin)
s = s[:a] + "\nconst SW = " + DATOS.read_text(encoding="utf-8") + ";\n" + s[b:]
HTML.write_text(s, encoding="utf-8")
print(f"{HTML} · {len(s)/1024/1024:.2f} MB")
