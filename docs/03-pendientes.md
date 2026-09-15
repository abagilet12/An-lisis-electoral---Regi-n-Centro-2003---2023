# Pendientes

## 1. Fuentes que hay que conseguir

Sin estos archivos la base no puede pasar de 3 departamentos a los 19 que fija el
encuadre. **El entorno de trabajo no tiene salida a los sitios oficiales**: la
política de red del entorno responde 403 a `argentina.gob.ar`,
`resultados.mininterior.gob.ar` y `datos.gob.ar`. La descarga la hace el
investigador; los archivos se suben a `Datos electorales 2003 - 2023` en Drive.

| Instancia | Qué hace falta | Dónde buscarlo |
|---|---|---|
| **Los 10 archivos `Votos por Localidad`** | Son la única fuente desagregada que existe hoy; están en Drive pero todavía no llegaron al repositorio | Drive: `Datos electorales 2007 - 2023` |
| **`presentacionDeResultados (39).xlsx`** | 2023 a nivel mesa: da 2023 provincial completo y el nomenclador circuito→localidad de toda la provincia | Drive: `Datos electorales 2007 - 2023` |
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

- ~~`src/ingest/dine_mesa.py`~~ — **hecho**, con pruebas. Esperando archivos.
- `src/nomenclador/` — falta el nomenclador **circuito → localidad** completo,
  versionado por elección. Hoy solo hay 30 circuitos mapeados, sobre la base
  2011. El de **departamentos** ya está hecho (`departamentos.py`), con los 19
  códigos oficiales de la DINE.
- ~~`src/ingest/control_provincial.py`~~ — **hecho**: nueve planillas cargadas,
  control provincial para 8 de las 12 instancias.

## 3. Decisiones metodológicas por tomar

- **Espacios políticos estables.** `dim_agrupacion.espacio_politico` está vacía.
  Hay que definir y documentar qué agrupaciones se consideran continuidad de
  cuáles a lo largo de la serie. Es la decisión más cargada de todo el proyecto y
  no se resuelve por código.
- **2003 con menor resolución.** Si no aparece una fuente por circuito, la
  alternativa es cargar 2003 a nivel departamento y declararlo explícitamente
  como serie de menor resolución. Nunca mezclarlo en silencio con el resto.
- **Paleta para 2003–2019.** Los colores oficiales de la DINE solo existen para
  2023. Para el resto de la serie hay que definir una paleta propia, y conviene
  resolverla junto con el mapeo de espacios políticos: si FPV y Unión por la
  Patria van a leerse como una continuidad, deberían compartir color.
- **Provisorio vs definitivo.** El archivo 2023 disponible es un recuento
  provisorio. Si aparece el definitivo, se reemplaza y se anota el cambio.
