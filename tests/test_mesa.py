"""Pruebas del ingestor a nivel mesa: las trampas del formato de la DINE."""

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "tests" / "fixtures"))

from generar_fixture_mesa import construir  # noqa: E402
from ingest.dine_mesa import leer_archivo  # noqa: E402

fallas = []


def chequear(condicion, mensaje):
    if not condicion:
        fallas.append(mensaje)


ruta = construir()
# El nomenclador solo conoce el circuito 0055.
ing = leer_archivo(ruta, nomenclador={"0055": "ESPERANZA"})

chequear(ing.fuente["eleccion_id"] == "2023-PASO", "instancia mal deducida")
chequear(ing.fuente["recuento"] == "PROVISORIO", "no detectó que el recuento es provisorio")

votos = {(h["localidad_id"], h["tipo_voto"], h["agrupacion_key"]): h["votos"] for h in ing.hechos}

# 1. Las listas internas de una agrupación se suman, no se duplican.
chequear(votos.get(("ESPERANZA", "POSITIVO", "UNION_POR_LA_PATRIA")) == 230,
         f"listas internas mal sumadas: {votos.get(('ESPERANZA','POSITIVO','UNION_POR_LA_PATRIA'))} (esperado 230)")

# 2. Otro distrito y otro cargo quedan afuera.
chequear(all(v < 7000 for v in votos.values()), "se coló una fila de otro distrito o de otro cargo")
chequear(not any(k[0] == "LA_PLATA" for k in votos), "se coló un departamento de otro distrito")

# 3. El padrón se cuenta una vez por mesa, no una vez por fila.
padron = {p["localidad_id"]: p for p in ing.padron}
chequear(padron["ESPERANZA"]["electores"] == 650,
         f"electores mal contados: {padron['ESPERANZA']['electores']} (esperado 650, no 1750)")
chequear(padron["ESPERANZA"]["mesas"] == 2, f"mesas mal contadas: {padron['ESPERANZA']['mesas']}")

# 4. Un circuito fuera del nomenclador no se pierde y conserva su departamento.
chequear(votos.get(("SIN_ASIGNAR_LAS_COLONIAS", "POSITIVO", "LA_LIBERTAD_AVANZA")) == 150,
         "se perdieron los votos de un circuito sin localidad")
sin_asignar = [h for h in ing.hechos if h["localidad_id"].startswith("SIN_ASIGNAR")]
chequear(sin_asignar and all(h["departamento_id"] in ("LAS_COLONIAS", "ROSARIO") for h in sin_asignar),
         "el circuito sin localidad perdió su departamento")
# Cada departamento tiene su propio cajón: si compartieran uno, los totales
# departamentales se mezclarían.
chequear(len({h["localidad_id"] for h in sin_asignar}) == 2,
         "los circuitos sin localidad de departamentos distintos cayeron en el mismo cajón")
chequear(ing.resumen["circuitos_sin_localidad"] == ["0500", "0999"],
         f"no reportó los circuitos sin localidad: {ing.resumen['circuitos_sin_localidad']}")

# 5. El departamento sale completo aunque no haya nomenclador: es el hallazgo
#    que permite cubrir los 19 departamentos sin mapear un solo circuito.
deptos = {h["departamento_id"] for h in ing.hechos}
chequear(deptos == {"LAS_COLONIAS", "ROSARIO"}, f"departamentos mal detectados: {deptos}")
total_las_colonias = sum(h["votos"] for h in ing.hechos if h["departamento_id"] == "LAS_COLONIAS")
chequear(total_las_colonias == 625,
         f"el total del departamento no cierra: {total_las_colonias} (esperado 625)")

# 6. Vocabulario de tipo de voto normalizado.
chequear(votos.get(("ESPERANZA", "BLANCO", None)) == 8, "'EN BLANCO' no se mapeó a BLANCO")
chequear(all(h["agrupacion_key"] is None for h in ing.hechos if h["tipo_voto"] != "POSITIVO"),
         "un voto no positivo quedó con agrupación")

if fallas:
    print("FALLAS:")
    for f in fallas:
        print(" -", f)
    sys.exit(1)
print(f"OK - {len(ing.hechos)} hechos, {ing.resumen['mesas']} mesas, "
      f"{ing.resumen['departamentos']} departamentos, "
      f"{len(ing.resumen['circuitos_sin_localidad'])} circuito(s) sin localidad")
