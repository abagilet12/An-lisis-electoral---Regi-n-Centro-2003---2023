# Inventario de datos — Presidente, Santa Fe, 2003-2023

Alcance de la investigación, según el plan (`Plan IHUCSO`) y el resumen del
Workshop CAI+D: **categoría electiva Presidente, provincia de Santa Fe,
2003-2023**, con resultados desagregados **por localidad, departamento y
provincia**. Todo lo que no es Santa Fe queda en `datos/reservados/` y no
entra en esta investigación.

## Universo: las elecciones presidenciales del período

Son 6 elecciones y 12 instancias de votación:

| Año | PASO | General | Balotaje |
|---|---|---|---|
| 2003 | no existía | sí | no hubo — Menem se retiró antes de la segunda vuelta |
| 2007 | no existía | sí | no hubo — la fórmula ganadora superó el umbral |
| 2011 | sí | sí | no hubo |
| 2015 | sí | sí | sí |
| 2019 | sí | sí | no hubo |
| 2023 | sí | sí | sí |

Las PASO se crean por Ley 26.571 (2009) y se aplican por primera vez en 2011.

## Qué hay disponible, y en qué nivel

Hay **dos niveles de agregación** con coberturas distintas. No son
intercambiables y conviene no confundirlos.

### Nivel provincial — distrito 21 completo

Fuente: "Consulta de Escrutinio por Zona" de la Justicia Nacional Electoral.
Ya incorporado en `datos/crudos/2023/`, procesado en `datos/procesados/`.

| Año | PASO | General | Balotaje |
|---|---|---|---|
| 2003 | — | ✗ | — |
| 2007 | — | ✗ | — |
| 2011 | ✗ | ✗ | — |
| 2015 | ✗ | ✗ | ✗ |
| 2019 | ✗ | ✗ | — |
| 2023 | ✓ | ✓ | ✓ |

**3 de 12 instancias.** Solo da el total provincial: no se puede desagregar.

### Nivel provincial — archivos de la DINE

Fuente: `resultados_<año>_<instancia>_presidente_y_vicepresidente.xlsx`,
archivos nacionales con una hoja por distrito. Se lee la de Santa Fe.
Procesados por `scripts/parse_resultados_dine.py`.

| Año | PASO | General | Balotaje |
|---|---|---|---|
| 2011 | ✓ | ✗ | — |
| 2015 | ✓ | ✗ | ✓ |

Aportan además la única fuente que vincula la **fórmula** (los nombres de
los candidatos) con la **agrupación** que la lleva: `formulas.csv`. Ese
puente es el que permite homologar 2007, donde las etiquetas son fórmulas,
con 2011 en adelante, donde son agrupaciones.

Sumando ambas fuentes, el nivel provincial cubre 6 de 12 instancias: PASO
2011, PASO y balotaje 2015, y las tres de 2023.

### Nivel localidad — 3 departamentos, 30 localidades

Fuente: archivos `Votos por Localidad - … - Presidente - Santa Fe.xlsx` en
Drive, construidos a partir de los datos por mesa de la DINE agregando por
circuito mediante un nomenclador circuito→localidad relevado a mano.

Cobertura geográfica: **Castellanos, Las Colonias y San Martín** (30 de 30
localidades del universo objetivo). Es la "zona núcleo", no la provincia
entera: Santa Fe tiene 19 departamentos.

| Año | PASO | General | Balotaje |
|---|---|---|---|
| 2003 | — | ✗ | — |
| 2007 | — | ✓ | — |
| 2011 | ✓ | ✓ | — |
| 2015 | ✓ | ✓ | ✓ |
| 2019 | ✓ | ✓ | — |
| 2023 | ✗ | ✓ | ✓ |

**10 de 12 instancias, todas incorporadas.** Faltan la general de 2003 y la
PASO de 2023.

Cada archivo trae seis hojas: votos por localidad y agrupación, agrupación
ganadora, totales por tipo de voto (blanco, nulo, impugnado, recurrido,
positivo, comando), electores y mesas, el nomenclador circuito-localidad, y
una hoja de metodología que documenta fuente y decisiones de procesamiento.

## Lo que falta

1. **General 2003, por localidad.** Es el hueco más costoso. La DINE publica
   datos desagregados recién desde 2011; para 2003 hay que ir a otra fuente
   (Atlas Electoral de Andy Tow, o el Tribunal Electoral de Santa Fe).
2. **PASO 2023, por localidad.** Hay que generarla desde el archivo por mesa
   de la DINE, igual que se hizo con la general 2023. El total provincial de
   esa instancia sí está, por escrutinio definitivo de la JNE.
3. **2011-2019 a nivel provincial**, si se quiere la serie provincial completa
   además de la de localidades. Se puede derivar de los archivos por mesa, no
   hace falta bajarla aparte.

## Advertencias de comparabilidad

- **Renumeración de circuitos en 2023.** El nomenclador circuito→localidad de
  2023 no sirve para 2011-2021 ni al revés: Santa Fe renumeró sus circuitos.
  Está reconstruido por separado para 2023.
- **2007 tiene otra fuente** (`Argentina07.mdb`, origen no verificado
  directamente) y viene por partido, no por fórmula, así que las agrupaciones
  están reconstruidas. Es el año menos homogéneo de la serie.
- **La oferta electoral no es comparable sin homologar.** En 2007 las
  etiquetas son fórmulas (`CRISTINA E. FERNANDEZ DE KIRCHNER-JULIO C.C.
  COBOS`); desde 2011 son agrupaciones (`ALIANZA FRENTE PARA LA VICTORIA`,
  luego `FRENTE DE TODOS`, luego `UNION POR LA PATRIA`). Sin una tabla de
  homologación no hay serie temporal posible.
- **No mezclar los dos niveles en un mismo gráfico.** El total provincial de
  2023 incluye los 19 departamentos; la serie por localidad cubre 3. Un
  porcentaje de uno no es comparable con el del otro.
