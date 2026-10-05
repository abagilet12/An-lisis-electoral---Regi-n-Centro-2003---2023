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


# Correcciones sobre el JavaScript original del tablero (idempotentes).
PARCHES = [
    # 1. Las capas 2003-2019 numeran los departamentos distinto que la geometría del mapa
    #    (001 Belgrano ... 022 Vera, contra 001 La Capital ... 019 San Lorenzo): el mapa
    #    por departamento pintaba cada polígono con datos de otro departamento.
    ("""  const dd={}; capa.forEach(f=>dd[f.c]=f.d);
  const out={};""",
     """  const ant=+clave.slice(0,4)<=2019;      // las capas 2003-2019 usan otra numeración de departamentos
  const dd={}; capa.forEach(f=>dd[f.c]= ant ? DEP_COD[DEP_ANT[f.d]] : f.d);
  const out={};"""),
    ("""function porUnidad(clave, nivel){""",
     """const DEP_ANT={"001":"Belgrano","002":"Caseros","003":"Castellanos","004":"Constitución","005":"Garay",
  "006":"General López","007":"General Obligado","008":"Iriondo","009":"La Capital","011":"Las Colonias",
  "012":"Nueve de Julio","013":"Rosario","016":"San Cristóbal","017":"San Javier","018":"San Jerónimo",
  "019":"San Justo","020":"San Lorenzo","021":"San Martín","022":"Vera"};
const DEP_COD={}; M.dep.forEach(g=>{ DEP_COD[g.n==="9 de Julio"?"Nueve de Julio":g.n]=g.d; });
function porUnidad(clave, nivel){"""),
    # 2. Epígrafe en la ficha histórica de un circuito
    ("""`<tbody>${filas}</tbody></table></div>`;""",
     """`<tbody>${filas}</tbody></table></div>`+
    `<p class="epi" style="padding:0 1rem .8rem">${EPI(["polar","dine23","cart"])}</p>`;"""),
]


def parchear(s):
    for viejo, nuevo in PARCHES:
        if nuevo in s:
            continue
        assert s.count(viejo) == 1, "no se encontró el fragmento: " + viejo[:50]
        s = s.replace(viejo, nuevo)
    return s


def main():
    s = HTML.read_text(encoding="utf-8")
    css = (PLANT / "fichas.css").read_text(encoding="utf-8")
    panel = (PLANT / "fichas.html").read_text(encoding="utf-8")
    js = (PLANT / "fichas.js").read_text(encoding="utf-8") + "\n" + (PLANT / "epigrafes.js").read_text(encoding="utf-8")
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
    gancho = '  if(p==="hall"){dibujarTiles();dibujarSerie();dibujarTramos();}\n'
    assert gancho in s
    if 'fichasMostrar(p)' not in s.replace(bloque, ""):
        s = s.replace(gancho, gancho + '  if(p==="ele"||p==="par") fichasMostrar(p);\n', 1)

    s = parchear(s)
    HTML.write_text(s, encoding="utf-8")
    print(f"{HTML} · {len(s)/1024/1024:.2f} MB")


if __name__ == "__main__":
    main()
