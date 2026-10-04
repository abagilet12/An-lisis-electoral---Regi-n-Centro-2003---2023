#!/usr/bin/env python3
"""
Agrega al tablero las pestañas «Elecciones» y «Partidos».

Toma salida/voto_santafesino.html, inserta (o reemplaza, si ya estaban) el
CSS, el HTML, los datos y el JavaScript de scripts/plantillas/ y los datos de
salida/datos_fichas.json. Se puede correr las veces que haga falta.

Uso: python3 scripts/agregar_pestanas.py [html] [datos_fichas.json]
"""
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PLANT = RAIZ / "scripts" / "plantillas"
HTML = Path(sys.argv[1]) if len(sys.argv) > 1 else RAIZ / "salida" / "voto_santafesino.html"
DATOS = Path(sys.argv[2]) if len(sys.argv) > 2 else RAIZ / "salida" / "datos_fichas.json"

TABS = ('    <button type="button" role="tab" id="tab-ele" aria-controls="pan-ele"\n'
        '            aria-selected="false" data-p="ele">Elecciones</button>\n'
        '    <button type="button" role="tab" id="tab-par" aria-controls="pan-par"\n'
        '            aria-selected="false" data-p="par">Partidos</button>\n')


def quitar(s, ini, fin):
    return re.sub(re.escape(ini) + r".*?" + re.escape(fin) + r"\n?", "", s, flags=re.S)


def main():
    s = HTML.read_text(encoding="utf-8")
    css = (PLANT / "fichas.css").read_text(encoding="utf-8")
    panel = (PLANT / "fichas.html").read_text(encoding="utf-8")
    js = (PLANT / "fichas.js").read_text(encoding="utf-8")
    datos = DATOS.read_text(encoding="utf-8")

    # 1. quitar versiones anteriores
    s = quitar(s, "/*FICHAS-CSS:INI*/", "/*FICHAS-CSS:FIN*/")
    s = quitar(s, "<!--FICHAS-HTML:INI-->", "<!--FICHAS-HTML:FIN-->")
    s = quitar(s, "/*FICHAS-JS:INI*/", "/*FICHAS-JS:FIN*/")
    s = re.sub(r'    <button type="button" role="tab" id="tab-ele".*?data-p="par">Partidos</button>\n',
               "", s, flags=re.S)

    # 2. pestañas
    ancla = 'data-p="hall">Hallazgos</button>\n'
    assert ancla in s, "no se encontró el botón de Hallazgos"
    s = s.replace(ancla, ancla + TABS, 1)

    # 3. CSS
    assert "</style>\n\n<div class=\"wrap\">" in s
    s = s.replace("</style>\n\n<div class=\"wrap\">",
                  f"/*FICHAS-CSS:INI*/\n{css}/*FICHAS-CSS:FIN*/\n</style>\n\n<div class=\"wrap\">", 1)

    # 4. paneles: entre el cierre del panel de Hallazgos y el cierre del contenedor
    ancla = "\n</div>\n</div>\n\n<script>"
    i = s.index(ancla)
    s = s[:i] + f"\n</div>\n<!--FICHAS-HTML:INI-->\n{panel}<!--FICHAS-HTML:FIN-->\n</div>\n\n<script>" + s[i + len(ancla):]

    # 5. JS: datos y lógica antes de las pestañas; registrar los paneles nuevos
    marca = "/* ---------- pestañas ---------- */"
    assert marca in s
    bloque = f"/*FICHAS-JS:INI*/\nconst R = {datos};\n{js}/*FICHAS-JS:FIN*/\n"
    s = s.replace(marca, bloque + marca, 1)
    s = s.replace('const PANEL = {datos:"#pan-datos", geo:"#pan-geo", hall:"#pan-hall"};',
                  'const PANEL = {datos:"#pan-datos", geo:"#pan-geo", hall:"#pan-hall", ele:"#pan-ele", par:"#pan-par"};')
    gancho = '  if(p==="hall"){dibujarSerie();dibujarVol();dibujarDes();dibujarDispersion();dibujarTramos();}\n'
    assert gancho in s
    if 'fichasMostrar(p)' not in s.replace(bloque, ""):
        s = s.replace(gancho, gancho + '  if(p==="ele"||p==="par") fichasMostrar(p);\n', 1)

    HTML.write_text(s, encoding="utf-8")
    print(f"{HTML} · {len(s)/1024/1024:.2f} MB")


if __name__ == "__main__":
    main()
