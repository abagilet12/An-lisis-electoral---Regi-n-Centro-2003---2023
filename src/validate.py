"""Controles de integridad sobre la base construida.

Emite docs/informe-validacion.md y termina con codigo distinto de cero si algun
control estructural falla. Los controles de cobertura no fallan: informan cuanto
falta cargar todavia.
"""

from __future__ import annotations

import difflib
import sqlite3
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

import comunes as c  # noqa: E402

BASE = RAIZ / "data" / "processed" / "santafe_electoral.db"
INFORME = RAIZ / "docs" / "informe-validacion.md"

#: Departamentos de la provincia de Santa Fe. Fija el denominador de cobertura.
DEPARTAMENTOS_SANTA_FE = [
    "9 de Julio", "Belgrano", "Caseros", "Castellanos", "Constitución", "Garay",
    "General López", "General Obligado", "Iriondo", "La Capital", "Las Colonias",
    "Rosario", "San Cristóbal", "San Javier", "San Jerónimo", "San Justo",
    "San Lorenzo", "San Martín", "Vera",
]


class Informe:
    def __init__(self) -> None:
        self.lineas: list[str] = []
        self.errores = 0

    def titulo(self, texto: str) -> None:
        self.lineas.append(f"\n## {texto}\n")

    def ok(self, texto: str) -> None:
        self.lineas.append(f"- OK — {texto}")

    def error(self, texto: str) -> None:
        self.errores += 1
        self.lineas.append(f"- **FALLA** — {texto}")

    def aviso(self, texto: str) -> None:
        self.lineas.append(f"- Aviso — {texto}")

    def texto(self, texto: str) -> None:
        self.lineas.append(texto)


def validar(con: sqlite3.Connection, inf: Informe) -> None:
    cur = con.cursor()

    # --- Estructurales ----------------------------------------------------
    inf.titulo("Controles estructurales")

    huerfanas = cur.execute("""
        SELECT COUNT(*) FROM hechos_votos h
        LEFT JOIN dim_localidad d ON d.localidad_id = h.localidad_id
        WHERE d.localidad_id IS NULL
    """).fetchone()[0]
    (inf.ok if huerfanas == 0 else inf.error)(
        f"localidades de hechos presentes en dim_localidad (huerfanas: {huerfanas})")

    duplicados = cur.execute("""
        SELECT COUNT(*) FROM (
            SELECT eleccion_id, localidad_id, tipo_voto, COALESCE(agrupacion_key,'')
            FROM hechos_votos
            GROUP BY 1,2,3,4 HAVING COUNT(*) > 1
        )
    """).fetchone()[0]
    (inf.ok if duplicados == 0 else inf.error)(
        f"sin filas duplicadas por eleccion/localidad/tipo/agrupacion (duplicados: {duplicados})")

    negativos = cur.execute("SELECT COUNT(*) FROM hechos_votos WHERE votos < 0").fetchone()[0]
    (inf.ok if negativos == 0 else inf.error)(f"sin votos negativos (encontrados: {negativos})")

    sin_asignar = cur.execute(
        "SELECT COUNT(*) FROM hechos_votos WHERE localidad_id = ?",
        (c.LOCALIDAD_SIN_ASIGNAR,)).fetchone()[0]
    if sin_asignar:
        inf.aviso(f"{sin_asignar} filas quedaron en {c.LOCALIDAD_SIN_ASIGNAR}: "
                  "hay circuitos sin localidad en el nomenclador")
    else:
        inf.ok("todas las filas tienen localidad asignada")

    # --- Votantes contra padron -------------------------------------------
    inf.titulo("Votantes y padron")

    excedidos = cur.execute("""
        SELECT eleccion_id, localidad, votantes, electores
        FROM v_totales_localidad
        WHERE electores IS NOT NULL AND votantes > electores
        ORDER BY votantes - electores DESC
    """).fetchall()
    if excedidos:
        inf.error(f"{len(excedidos)} localidad(es) con mas votantes que electores")
        for elec, loc, votantes, electores in excedidos[:10]:
            inf.texto(f"  - {elec} / {loc}: {votantes} votantes sobre {electores} electores")
    else:
        inf.ok("en ninguna localidad los votantes superan a los electores")

    sin_padron = cur.execute("""
        SELECT COUNT(*) FROM v_totales_localidad WHERE electores IS NULL
    """).fetchone()[0]
    if sin_padron:
        inf.aviso(f"{sin_padron} combinaciones eleccion/localidad sin padron declarado")
    else:
        inf.ok("todas las combinaciones eleccion/localidad tienen padron")

    # --- Incidencias arrastradas de la ingesta ----------------------------
    inf.titulo("Descuadres detectados en la ingesta")
    incidencias = cur.execute("""
        SELECT eleccion_id, localidad_id, control, esperado, obtenido, diferencia
        FROM incidencias ORDER BY ABS(diferencia) DESC
    """).fetchall()
    if incidencias:
        inf.error(f"{len(incidencias)} descuadre(s) entre el total declarado y la suma por agrupacion")
        for elec, loc, control, esperado, obtenido, dif in incidencias[:15]:
            inf.texto(f"  - {elec} / {loc} ({control}): declarado {esperado}, "
                      f"sumado {obtenido}, diferencia {dif:+d}")
    else:
        inf.ok("los positivos declarados coinciden con la suma por agrupacion")

    # --- Nombres sospechosamente parecidos --------------------------------
    inf.titulo("Posibles duplicados por nombre")
    localidades = [f"{d}|{l}" for d, l in cur.execute(
        "SELECT departamento_id, localidad FROM dim_localidad ORDER BY localidad")]
    parecidos = []
    for i, a in enumerate(localidades):
        for b in localidades[i + 1:]:
            da, na = a.split("|", 1)
            db, nb = b.split("|", 1)
            if da != db:
                continue
            ratio = difflib.SequenceMatcher(None, c.clave(na) or "", c.clave(nb) or "").ratio()
            if 0.90 <= ratio < 1.0:
                parecidos.append((da, na, nb, ratio))
    if parecidos:
        inf.aviso(f"{len(parecidos)} par(es) de localidades con nombres casi identicos, revisar a mano")
        for depto, na, nb, ratio in parecidos[:15]:
            inf.texto(f"  - {depto}: '{na}' vs '{nb}' ({ratio:.2f})")
    else:
        inf.ok("sin nombres de localidad casi identicos dentro de un mismo departamento")

    # --- Cobertura (informa, no falla) ------------------------------------
    inf.titulo("Cobertura")

    faltantes = [e for (e,) in cur.execute(
        "SELECT eleccion_id FROM dim_eleccion WHERE cargada = 0 ORDER BY orden_cronologico")]
    cargadas = 12 - len(faltantes)
    inf.texto(f"\nInstancias cargadas: **{cargadas} de 12**.")
    if faltantes:
        inf.texto(f"Faltan: {', '.join(faltantes)}.")

    deptos = {d for (d,) in cur.execute("SELECT DISTINCT departamento_id FROM hechos_votos")}
    esperados = {c.clave(d) for d in DEPARTAMENTOS_SANTA_FE}
    inf.texto(f"\nDepartamentos con datos: **{len(deptos)} de 19**.")
    sin_datos = sorted(d for d in DEPARTAMENTOS_SANTA_FE if c.clave(d) not in deptos)
    if sin_datos:
        inf.texto(f"Sin datos: {', '.join(sin_datos)}.")
    intrusos = deptos - esperados - {c.clave(c.LOCALIDAD_SIN_ASIGNAR)}
    if intrusos:
        inf.error(f"departamentos que no pertenecen a Santa Fe: {sorted(intrusos)}")

    inf.texto("\n| Instancia | Departamentos | Localidades | Agrupaciones | Votos |")
    inf.texto("|---|---:|---:|---:|---:|")
    for elec, nd, nl, na, votos in cur.execute("""
        SELECT eleccion_id,
               COUNT(DISTINCT departamento_id),
               COUNT(DISTINCT localidad_id),
               COUNT(DISTINCT agrupacion_key),
               SUM(votos)
        FROM hechos_votos
        GROUP BY eleccion_id
        ORDER BY anio, instancia
    """):
        inf.texto(f"| {elec} | {nd} | {nl} | {na} | {votos:,} |".replace(",", "."))

    inf.titulo("Pendiente")
    inf.texto("- Contraste contra los totales provinciales de la DINE: requiere cargar las "
              "planillas por distrito (`src/ingest/control_provincial.py`, no implementado aun).")
    inf.texto("- `dim_agrupacion.espacio_politico` esta vacia: el mapeo de espacios politicos "
              "estables se define en la etapa siguiente.")


def main() -> int:
    if not BASE.exists():
        print(f"No existe {BASE}. Corre primero: python3 src/build_db.py")
        return 1
    con = sqlite3.connect(BASE)
    inf = Informe()
    inf.texto("# Informe de validacion\n")
    inf.texto("Generado por `src/validate.py`. No editar a mano.")
    validar(con, inf)
    con.close()

    INFORME.parent.mkdir(parents=True, exist_ok=True)
    INFORME.write_text("\n".join(inf.lineas) + "\n", encoding="utf-8")
    print(f"Informe escrito en {INFORME.relative_to(RAIZ)} — {inf.errores} falla(s)")
    return 1 if inf.errores else 0


if __name__ == "__main__":
    sys.exit(main())
