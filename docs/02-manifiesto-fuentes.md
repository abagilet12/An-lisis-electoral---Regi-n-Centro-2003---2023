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

Verificado hoja por hoja sobre los archivos ya descargados: la hoja `Santa Fe` de
cada libro tiene entre 11 y 27 filas con contenido y ninguna menciona un
departamento ni un circuito.

No sirven como fuente de la base, pero sí como **totales de control**: el total
provincial por agrupación que arroje la base debe coincidir con ellas. Ese
contraste lo hace `src/ingest/control_provincial.py`, ya implementado y cargado.

### Estado de la capa de control

Nueve planillas cargadas, con total provincial para **8 de las 12 instancias**:
2003-GENERAL, 2007-GENERAL, 2011-PASO, 2011-GENERAL, 2015-PASO, 2015-GENERAL,
2015-BALLOTAGE y 2019-GENERAL. Falta control provincial de 2019-PASO (el archivo
disponible es solo total país) y de las tres instancias de 2023.

Las 16 hojas leídas **cuadran**: positivos más blancos más nulos da exactamente
el total de votantes declarado, y los votantes nunca superan a los electores.

Tres particularidades de estas planillas que el ingestor contempla:

- **La instancia no se deduce del nombre del archivo**, que es irregular, sino de
  la fecha que la propia hoja declara en su encabezado.
- **2011-PASO intercala una fila `VOTOS VÁLIDOS`** (positivos + blancos) entre las
  agrupaciones y el pie. Tomada por una agrupación duplicaba los votos positivos
  de la provincia. Hay un test de regresión para ese caso y el ingestor ahora
  **falla** ante cualquier etiqueta `VOTOS …` que no reconozca, en lugar de
  cargarla como un partido inexistente.
- **Las hojas `Nacionales` de 2003 y 2007 son un índice** de fórmulas y partidos
  componentes, sin columna de votos. Se omiten, y la omisión se informa al
  construir la base en vez de pasar inadvertida.

## El formato a nivel mesa

`presentacionDeResultados` es el formato que habilita la cobertura provincial.
Trae una fila por mesa × cargo × lista × tipo de voto, y lo lee
`src/ingest/dine_mesa.py`.

**Su columna `seccion_nombre` es el departamento.** Eso significa que este
formato da los **19 departamentos sin necesidad de ningún nomenclador**: solo la
desagregación por localidad depende del mapeo circuito → localidad. Es el
hallazgo que define la estrategia: cada archivo a nivel mesa que consigamos
aporta cobertura departamental completa de inmediato, y la localidad se va
completando a medida que crece el nomenclador.

Cuatro trampas del formato que el ingestor contempla, todas con test:

- En las **PASO cada agrupación presenta varias listas internas**; el total de la
  agrupación es la suma de sus listas.
- El **padrón de la mesa se repite en cada fila** de esa mesa: sumarlo tal cual lo
  multiplicaría por la cantidad de listas. Se cuenta una vez por mesa.
- El archivo trae **todos los distritos y todos los cargos**: se filtra Santa Fe y
  presidente.
- Un **circuito ausente del nomenclador no se descarta**: se imputa a la localidad
  sin asignar *de su departamento*, y se informa al construir la base.

## Nomencladores

`AmbitosElectorales_2023_Generales.csv` — nomenclador oficial de distritos y
secciones. En Santa Fe la sección es el departamento: da los 19 con su código
oficial (1 = La Capital … 19 = San Lorenzo), que alimenta `dim_departamento`.

`Colores_2023.csv` — colores oficiales de las agrupaciones, 20 para Santa Fe.
Alimenta `dim_color_agrupacion` y trae el `agrupacion_id` numérico, que es la
clave con la que vienen los resultados a nivel mesa de 2023. El color es por
distrito: se carga filtrando Santa Fe. Solo cubre 2023.

## Capas geográficas

En `Datos electorales 2007 - 2023`: `departamento.zip`, `provincia.zip`,
`pais.zip`, `linea_de_limite_070110.geojson` y `linea_de_limite_070111.zip`
(IGN). Van a `data/geo/` cuando se construyan los mapas.
