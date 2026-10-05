# Replicar el análisis en Córdoba y Entre Ríos

Objetivo: reutilizar la estructura del análisis (bases → procesamiento → tablero) para otras provincias de la Región Centro. Esta
nota deja asentado qué se reutiliza tal cual, qué cambia y qué falta.

## Cadena completa (Santa Fe)

| Etapa | Entradas | Scripts | Salidas |
|---|---|---|---|
| 1. Resultados por mesa, circuito y localidad | DINE, PolAr, archivos por localidad | `scripts/parse_*.py`, `scripts/agregar_mesa_a_*.py`, `src/` | `datos/procesados/resultados_*.csv` |
| 2. Homologación | tabla de homologación | `scripts/homologar.py` | `serie_homologada.csv` |
| 3. Familias, color y escala ideológica | `homologacion_agrupaciones.csv`, `colores_familias.csv`, `ubicacion_familias.csv` | (tablas de decisión) | `docs/CRITERIOS_COLOR.md`, `docs/CRITERIO_IDEOLOGICO_BOBBIO.md` |
| 4. Cartografía de circuitos | repositorio `circuitos_electorales_AR` | `scripts/construir_capa_circuitos.py` | `datos/geo/circuitos/*_reconstruido.geojson` |
| 5. Censo 2022 | radios censales y base por provincia (INDEC) | `scripts/asignar_circuitos_a_localidad.py` | `circuito_localidad.csv`, `poblacion_gobiernos_locales_censo2022.csv` |
| 6. Indicadores | los anteriores | `preparar_datos_analisis.py`, `construir_datos_fichas.py`, `asignar_familia_fichas.py`, `construir_tamano_lugar.py`, `construir_swing.py` | `salida/datos_*.json` |
| 7. Verificaciones | los anteriores | `verificar_derecha_libertaria.py`, `verificar_poblacion_censo.py` | informes y CSV de control |
| 8. Tablero | los JSON | `agregar_pestanas.py`, `agregar_tamano_lugar.py`, `agregar_swing.py` | `salida/voto_santafesino.html` |

## Qué es específico de Santa Fe y hay que parametrizar

- Código de provincia en las URL y filtros del censo (`82` para Santa Fe; Córdoba `14`, Entre Ríos `30`) y nombre del archivo
  `82-santa-fe-2022.zip`.
- `DEPTOS` (departamentos con resultados por localidad) en `scripts/asignar_circuitos_a_localidad.py`.
- Códigos de departamento de la cartografía (`departamentos_codigos_cartografia.csv`) y las capas por año.
- Distrito electoral en los filtros de la DINE (Santa Fe es el distrito 21; Córdoba, 04; Entre Ríos, 08).
- Textos del tablero que nombran a Santa Fe, sus departamentos o sus cifras (las interpretaciones de «Evolución del voto» y del
  marco de referencia).

## Qué falta para replicar sin trabajo manual

1. **Constructor de los datos del mapa** (`M` en el HTML: capas, departamentos, votos por circuito, padrón, tabla por elección y
   enlace histórico). No está en el repositorio: el HTML conserva el resultado. El enlace histórico entre circuitos se extrajo a
   `datos/referencia/enlace_circuitos.csv`, pero no hay script que lo genere. Conviene escribirlo antes de replicar.
2. **Parametrizar los scripts** por provincia con un archivo de configuración (distrito, código INDEC, años, departamentos).
3. **Separar los textos** del HTML de las cifras para que se regeneren con los datos.

## Criterios que se mantienen sin cambios

Colores y etiquetas de familias, criterio de la derecha libertaria, escala ideológica (Bobbio), escala demográfica, elecciones
definitivas, criterios de redacción, márgenes y paleta (`docs/ESTRUCTURA_TABLERO.md`).
