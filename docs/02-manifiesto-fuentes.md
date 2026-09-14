# Manifiesto de fuentes

Qué archivo respalda cada una de las 12 instancias. Las fuentes originales **no
se versionan en Git** (`data/raw/` está en `.gitignore`): pesan cientos de
megabytes. Este documento y la tabla `fuentes` de la base — que guarda el
`sha256` de cada archivo efectivamente procesado — son la garantía de
trazabilidad.

Ubicación en Drive: `Mi Unidad / CAI+D FHUC-Pol. /`

## Estado por instancia

| Instancia | Fuente | Cobertura | Estado |
|---|---|---|---|
| 2003-GENERAL | — | — | **Sin fuente desagregada identificada** |
| 2007-GENERAL | `Votos por Localidad - 2007 - Presidente - Santa Fe.xlsx` (derivado de `Argentina07.mdb`) | 3 deptos / 30 localidades | Parcial |
| 2011-PASO | `Votos por Localidad - PASO 2011 - …xlsx` | 3 deptos / 30 localidades | Parcial |
| 2011-GENERAL | `Votos por Localidad - Generales 2011 - …xlsx` | 3 deptos / 30 localidades | Parcial |
| 2015-PASO | `Votos por Localidad - PASO 2015 - …xlsx` | 3 deptos / 30 localidades | Parcial |
| 2015-GENERAL | `Votos por Localidad - Generales 2015 - …xlsx` | 3 deptos / 30 localidades | Parcial |
| 2015-BALLOTAGE | `Votos por Localidad - Ballotage 2015 - …xlsx` (derivado de `presentacionDeResultadosBallotage_SantaFe_2015.csv`, DINE) | 3 deptos / 30 localidades | Parcial |
| 2019-PASO | `Votos por Localidad - PASO 2019 - …xlsx` | 3 deptos / 30 localidades | Parcial |
| 2019-GENERAL | `Votos por Localidad - Generales 2019 - …xlsx` | 3 deptos / 30 localidades | Parcial |
| 2023-PASO | `presentacionDeResultados (39).xlsx` (nivel mesa, recuento **provisorio**) | provincia completa | Disponible, sin procesar |
| 2023-GENERAL | `Votos por Localidad - Generales 2023 - …xlsx` | 3 deptos / 30 localidades | Parcial |
| 2023-BALLOTAGE | `Votos por Localidad - Segunda Vuelta 2023 - …xlsx` | 3 deptos / 30 localidades | Parcial |

"3 deptos" son Castellanos, Las Colonias y San Martín.

## Los archivos derivados

Los diez `Votos por Localidad - … - Presidente - Santa Fe.xlsx` son productos ya
procesados en etapas previas del proyecto. Traen seis hojas; el pipeline usa
cinco e ignora `Agrupacion Ganadora por Localidad` por ser derivable. La hoja
`Metodologia` de cada libro documenta su fuente y se lee automáticamente para
poblar la tabla `fuentes`.

## Totales de control (no alimentan la base)

Las nueve planillas DINE de `Datos electorales 2003 - 2023` (2003, 2007, 2011
PASO y generales, 2015 PASO / generales / segunda vuelta, 2019) **están agregadas
por distrito**: no traen departamento ni localidad. Se verificó buscando
"Castellanos" en el texto completo de las nueve, sin resultados.

No sirven como fuente de la base, pero sí como **totales de control**: el total
provincial por agrupación que arroje la base debe coincidir con ellas. Ese
contraste lo hará `src/ingest/control_provincial.py`, todavía no implementado.

`AmbitosElectorales_2023_Generales.csv` es el nomenclador oficial de distritos y
secciones de 2023; sirve para validar nombres de departamento.

## Capas geográficas

En `Datos electorales 2007 - 2023`: `departamento.zip`, `provincia.zip`,
`pais.zip`, `linea_de_limite_070110.geojson` y `linea_de_limite_070111.zip`
(IGN). Van a `data/geo/` cuando se construyan los mapas.
