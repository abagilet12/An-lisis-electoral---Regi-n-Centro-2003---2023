#!/usr/bin/env python3
"""
Cruza los partidos integrantes de las alianzas 2003-2011 (composicion_alianzas.csv,
tomados de los Excel de resultados de la DINE) con el registro oficial de partidos
(UEEDA, DINE, cierre 30/09/2026).

Salida: datos/referencia/partidos_integrantes_vs_registro.csv

El registro cubre solo los partidos vigentes hoy y su historial desde junio de 2018.
Un partido que no figura puede haber existido antes de 2018 y haberse extinguido.
"fecha_reconocimiento" puede ser la de un nuevo reconocimiento y no la de fundación
(la UCEDE figura en 2023, por ejemplo). El cruce se hace contra los partidos de orden nacional; los partidos provinciales
(con provincia entre paréntesis) se marcan sin evaluar.
"""
import csv
import re
import unicodedata
from pathlib import Path

import openpyxl

RAIZ = Path(__file__).resolve().parent.parent
REG = RAIZ / "datos" / "crudos" / "dine_registro_partidos"
REF = RAIZ / "datos" / "referencia"

ALIAS = {  # nombre en los resultados de la DINE -> nombre legal en el registro
    "JUSTICIALISTA": "PARTIDO JUSTICIALISTA",
    "FRENTE GRANDE": "PARTIDO FRENTE GRANDE",
    "SOCIALISTA": "PARTIDO SOCIALISTA",
    "INTRANSIGENTE": "PARTIDO INTRANSIGENTE",
    "COMUNISTA": "PARTIDO COMUNISTA",
    "HUMANISTA": "PARTIDO HUMANISTA",
    "SOLIDARIO": "PARTIDO SOLIDARIO",
    "CONSERVADOR POPULAR": "PARTIDO CONSERVADOR POPULAR",
    "DEMOCRATA CRISTIANO": "PARTIDO DEMOCRATA CRISTIANO",
    "UNION CIVICA RADICAL": "UNION CIVICA RADICAL",
    "FEDERAL": "PARTIDO FEDERAL",
    "OBRERO": "PARTIDO OBRERO",
    "DE LA VICTORIA": "PARTIDO DE LA VICTORIA",
    "COALICION CIVICA AFIRMACION PARA UNA REPUBLICA IGUALITARIA": "COALICION CIVICA - AFIRMACION PARA UNA REPUBLICA IGUALITARIA (ARI)",
    "MOVIMIENTO SOCIALISTA DE LOS TRABAJADORES": "MOVIMIENTO SOCIALISTA DE LOS TRABAJADORES",
    "UNION DEL CENTRO DEMOCRATICO": "UNION DEL CENTRO DEMOCRATICO",
    "UNION POPULAR": "UNION POPULAR FEDERAL",
}


# Nombres genéricos que usaron partidos distintos en distintos años y distritos.
AMBIGUOS = {"POPULAR", "AUTONOMISTA"}


def norm(s):
    s = unicodedata.normalize("NFD", str(s)).encode("ascii", "ignore").decode().upper()
    s = re.sub(r"\(.*?\)", " ", s)
    return re.sub(r"\s+", " ", re.sub(r"[^A-Z0-9 ]", " ", s)).strip()


def cargar(archivo, hoja):
    it = openpyxl.load_workbook(REG / archivo, read_only=True, data_only=True)[hoja].iter_rows(values_only=True)
    cab = next(it)
    return [dict(zip(cab, r)) for r in it if r[0]]


def declarado(p):
    m = re.search(r"\((.*?)\)", p)
    return m.group(1) if m else ""


def main():
    vig = cargar("UEEDA_Partidos_Vigentes_30_09_2026.xlsx", "Partidos vigentes")
    his = cargar("UEEDA_historizacion_partidos_vigentes_30_09_2026.xlsx", "Historización")
    nac = {}
    for r in his:
        if r["orden"] == "NACIONAL":
            nac.setdefault(norm(r["partido_politico"]), []).append(r)
    for r in vig:
        if r["orden"] == "NACIONAL":
            nac.setdefault(norm(r["partido_politico"]), []).append(r)

    filas = []
    with open(REF / "composicion_alianzas.csv", encoding="utf8") as fh:
        for c in csv.DictReader(fh):
            p = c["partido_integrante"]
            ambito = declarado(p) or "Orden Nacional (sin aclarar)"
            clave = norm(p)
            provincial = bool(re.search(r"\((?!Orden Nacional)[^)]*[A-Za-zÁÉÍÓÚáéíóú]", p)) and "Orden Nacional" not in p
            reg, tipo = None, ""
            if not provincial:
                if clave in nac:
                    reg, tipo = nac[clave], "exacta"
                elif ("PARTIDO " + clave) in nac:
                    reg = nac["PARTIDO " + clave]
                    tipo = "probable (revisar)" if clave in AMBIGUOS else "agregando 'Partido'"
                elif clave in ALIAS and norm(ALIAS[clave]) in nac:
                    reg, tipo = nac[norm(ALIAS[clave])], "probable (revisar)"
            if reg:
                ult = reg[-1]
                vig_hoy = any(x.get("vigente_ultimo_cierre") == "SI" or "fecha_cierre" in x for x in reg)
                estado = ("vigente al 30/09/2026" if vig_hoy else
                          f"baja en el registro (último cierre {ult.get('disponible_hasta')})")
                filas.append([c["anio"], c["instancia"], c["alianza"], p, ambito, ult["partido_politico"],
                              ult.get("sigla") or "", ult["fecha_reconocimiento"], tipo, estado, ult["idpartido"]])
            else:
                nota = ("partido de otro distrito; no evaluado" if provincial
                        else "no figura en el registro 2018-2026 (puede haberse extinguido)")
                filas.append([c["anio"], c["instancia"], c["alianza"], p, ambito, "", "", "", "", nota, ""])
    with open(REF / "partidos_integrantes_vs_registro.csv", "w", newline="", encoding="utf8") as fh:
        w = csv.writer(fh)
        w.writerow(["anio", "instancia", "alianza", "partido_en_resultados_dine", "ambito_declarado",
                    "nombre_legal_registro", "sigla", "fecha_reconocimiento", "tipo_coincidencia", "estado_registro", "idpartido"])
        w.writerows(filas)
    n = sum(1 for f in filas if f[5])
    print(len(filas), "filas;", n, "con coincidencia en el registro")


if __name__ == "__main__":
    main()
