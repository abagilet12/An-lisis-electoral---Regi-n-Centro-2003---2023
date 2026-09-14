# Pendientes

## 1. Fuentes que hay que conseguir

Sin estos archivos la base no puede pasar de 3 departamentos a los 19 que fija el
encuadre. **El entorno de trabajo no tiene salida a los sitios oficiales**: la
política de red del entorno responde 403 a `argentina.gob.ar`,
`resultados.mininterior.gob.ar` y `datos.gob.ar`. La descarga la hace el
investigador; los archivos se suben a `Datos electorales 2003 - 2023` en Drive.

| Instancia | Qué hace falta | Dónde buscarlo |
|---|---|---|
| 2003-GENERAL | Cualquier fuente por circuito o departamento | DINE histórico, Tribunal Electoral de Santa Fe, Atlas Electoral |
| 2007-GENERAL | `Argentina07.mdb` (el usado para el derivado) | Archivo propio del investigador |
| 2011 PASO y generales | Resultados por mesa o circuito, Santa Fe | DINE |
| 2015 PASO, generales, ballotage | Ídem (el derivado cita `presentacionDeResultadosBallotage_SantaFe_2015.csv`) | resultados.mininterior.gob.ar |
| 2019 PASO y generales | Ídem | resultados.mininterior.gob.ar |
| 2023 PASO, generales, ballotage | Versión **definitiva** por mesa (hoy solo hay el provisorio de PASO) | resultados.gob.ar |
| Localidades | Listado oficial de localidades por departamento de Santa Fe | IPEC / IGN |

Si el entorno se configurara con una política de red que habilite esos dominios,
la descarga podría automatizarse desde el propio pipeline.

## 2. Código por escribir

- `src/ingest/dine_mesa.py` — ingesta del formato mesa (`presentacionDeResultados`):
  filtra distrito Santa Fe y cargo presidente, y agrega mesa → circuito →
  localidad. Es el camino a los 19 departamentos.
- `src/nomenclador/` — construcción del nomenclador circuito → localidad completo
  para la provincia, versionado por elección. Hoy solo hay 30 circuitos mapeados,
  sobre la base 2011.
- `src/ingest/control_provincial.py` — carga de las planillas DINE por distrito
  como totales de control.

## 3. Decisiones metodológicas por tomar

- **Espacios políticos estables.** `dim_agrupacion.espacio_politico` está vacía.
  Hay que definir y documentar qué agrupaciones se consideran continuidad de
  cuáles a lo largo de la serie. Es la decisión más cargada de todo el proyecto y
  no se resuelve por código.
- **2003 con menor resolución.** Si no aparece una fuente por circuito, la
  alternativa es cargar 2003 a nivel departamento y declararlo explícitamente
  como serie de menor resolución. Nunca mezclarlo en silencio con el resto.
- **Provisorio vs definitivo.** El archivo 2023 disponible es un recuento
  provisorio. Si aparece el definitivo, se reemplaza y se anota el cambio.
