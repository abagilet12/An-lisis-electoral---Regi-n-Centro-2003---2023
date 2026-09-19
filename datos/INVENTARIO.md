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

### Nivel provincial — fuentes transcriptas

Para 2003 no hay fuente procesable: la DINE arranca en 2011 y la Consulta de
Escrutinio por Zona tampoco lo cubre. El dato se transcribió a mano desde una
tabla de resultados y se validó con tres controles aritméticos que dan
exactos (ver `datos/crudos/transcripciones/README.md`).

| Año | PASO | General | Balotaje |
|---|---|---|---|
| 2003 | no existía | ✓ | no hubo |

Con esto **el nivel provincial cubre 7 de las 12 instancias** del período.

### Nivel circuito — 2023, desde los archivos por mesa de la DINE

Fuente: los CSV por mesa, agregados por
`scripts/agregar_mesa_a_circuito.py`. **El circuito es la unidad geográfica
del mapa electoral y viene identificado en el propio archivo**, así que este
nivel no depende de ningún nomenclador y cubre los 19 departamentos.

| Año | PASO | General | Balotaje |
|---|---|---|---|
| 2023 | ✓ | ✓ | ✗ |

Junto con los nueve de PolAr, **el nivel circuito cubre 11 de las 12
instancias**. Solo falta el balotaje 2023.

**No se puede obtener por la API**: comprobado en una misma corrida, la
general devuelve 380 circuitos en el muestreo y la segunda vuelta cero, con
los 523 códigos reales y pasando `seccionId` como padre. La única vía es su
archivo por mesa, el equivalente de
`ResultadoElectorales_2023_Generales.csv` para la segunda vuelta.

Verificado: los 523 circuitos suman exactamente el total provincial, y el
padrón agregado (2.822.834) coincide con el del escrutinio definitivo de la
JNE (2.822.833). Es recuento provisorio: la brecha con el definitivo es de
36.944 votos (−2,08 %) en las seis fuerzas principales.

`nomenclador_circuitos_2023.csv` lista los 523 circuitos con departamento,
padrón y mesas. La columna `localidad` está poblada en 30 y vacía en 493:
esas son, exactamente, las que faltan relevar a mano en padron.gob.ar.

### Nivel circuito — toda la provincia, 2003-2019

Fuente: escrutinios provisorios de
[PoliticaArgentina/data_warehouse](https://github.com/PoliticaArgentina/data_warehouse),
que a su vez vienen del **Atlas Electoral de Andy Tow** (2003-2017) y, para
2019, de los paquetes de @pmoracho. Datos **a nivel mesa**, agregados por
`scripts/parse_polar.py`.

| Año | PASO | General | Balotaje |
|---|---|---|---|
| 2003 | no existía | ✓ | no hubo |
| 2007 | no existía | ✓ | no hubo |
| 2011 | ✓* | ✓* | no hubo |
| 2015 | ✓ | ✓ | ✓ |
| 2019 | ✓ | ✓ | no hubo |

**Nueve instancias, entre 516 y 527 circuitos, los 19 departamentos.** Es la
fuente que cierra los agujeros estructurales: **2003 y 2007 desagregados**,
que ningún organismo publica.

Validado: el padrón agregado coincide al elector con las cifras oficiales
(2003: 2.235.568 · 2011: 2.440.284 · 2015: 2.687.061).

**\* 2011 viene partido en 22 unidades**, igual que en la API: misma anomalía
en ambas fuentes, lo que la confirma como propia del dato y no del
procesamiento.

Es recuento **provisorio**. En 2003 da 2,32 % *más* que el definitivo — al
revés que los archivos de la DINE, que dan de menos.

Dos detalles de la fuente resueltos en el parser: en la general 2019 los
códigos de lista de los datos (`00001`-`00010`) no coinciden con los del
diccionario (`00024`-`00108`), porque ese año se reconstruyó de otro origen;
el mapeo se resolvió cotejando totales contra la API, que sí trae nombres, y
se confirmó viendo que en Rosario el orden se invierte igual en ambas
fuentes. Y **2007 viene por partido, no por fórmula**, así que las etiquetas
son partidos y no candidatos.

### Nivel departamento — toda la provincia, vía API

Fuente: la API de la DINE, recolectada con
`notebooks/extraccion_api_dine.ipynb` y procesada por
`scripts/parse_api_dine.py`.

| Año | PASO | General | Balotaje |
|---|---|---|---|
| 2011 | ✓* | ✓* | — |
| 2015 | ✓ | ✓ | ✓ |
| 2019 | ✓ | ✓ | — |
| 2023 | ✓ | ✓ | ✓ |

**10 instancias, provincia entera.** Es el nivel intermedio que faltaba: con
esto el universo `provincia_completa` deja de ser 2003 y 2023 sueltos y pasa
a ser una serie.

Verificado: 2015, 2019 y 2023 traen los 19 departamentos y el padrón cierra
exacto contra la referencia provincial (2023 general: 8.332 mesas, 2.827.794
electores).

**\* 2011 viene partido en 22 unidades, no en los 19 departamentos.** El
padrón total cierra exacto contra el archivo oficial (2.440.284 electores),
así que la partición es completa, pero sus unidades no son los departamentos
de los demás años. La columna `particion_comparable` lo marca.

Es **recuento provisorio**: en la general 2023 da 18.456 votos menos que el
escrutinio definitivo (−0,90 %).

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

**11 de 12 instancias.** Diez salen de los `.xlsx`; la PASO 2023 se agregó
desde el CSV por mesa con `scripts/agregar_mesa_a_localidad.py`, que agrupa
las mesas por circuito y los circuitos por localidad usando el nomenclador.
Solo falta la general de 2003.

La tabla unificada es `datos/procesados/serie_localidad.csv`, que une ambas
fuentes con las columnas `fuente` y `recuento_tipo`.

Cada archivo trae seis hojas: votos por localidad y agrupación, agrupación
ganadora, totales por tipo de voto (blanco, nulo, impugnado, recurrido,
positivo, comando), electores y mesas, el nomenclador circuito-localidad, y
una hoja de metodología que documenta fuente y decisiones de procesamiento.

## Lo que falta

1. **General 2003, desagregada.** El total provincial ya está (transcripto).
   Falta la desagregación por circuito o localidad, que la DINE no cubre
   porque arranca en 2011. Hay que ir a otra fuente: Atlas Electoral de Andy
   Tow o Tribunal Electoral de Santa Fe.
2. **Confirmar si existe el escrutinio definitivo por mesa.** El CSV por
   mesa que se usó para la PASO 2023 declara `recuento_tipo = PROVISORIO`.
   Que esa columna exista sugiere que hay una variante `DEFINITIVO`; si está
   disponible para descarga, conviene rehacer con ella toda la serie por
   localidad, porque el provisorio difiere del definitivo (en el total
   provincial de la PASO 2023, entre 2 y 2,3 % en las principales fuerzas).
3. **2011-2019 a nivel provincial**, si se quiere la serie provincial completa
   además de la de localidades. Se puede derivar de los archivos por mesa, no
   hace falta bajarla aparte.

## Advertencias de comparabilidad

- **Renumeración de circuitos en 2023.** El nomenclador circuito→localidad de
  2023 no sirve para 2011-2021 ni al revés: Santa Fe renumeró sus circuitos.
  Está reconstruido por separado para 2023.
- **El recuento provisorio no es el definitivo.** Ver
  [`docs/NOTA_METODOLOGICA_2023.md`](../docs/NOTA_METODOLOGICA_2023.md), que
  deja constancia de que trabajar 2023 con datos provisorios responde a la
  falta de publicación del escrutinio definitivo desagregado por parte de los
  organismos responsables, y no a una decisión de esta investigación. La PASO 2023 por localidad
  viene del recuento provisorio, y las hojas de metodología de los `.xlsx`
  apuntan a archivos de la misma familia, así que probablemente toda la serie
  por localidad lo sea. El nivel provincial, en cambio, usa el escrutinio
  definitivo de la JNE. No mezclar ambos en un mismo cálculo: la columna
  `recuento_tipo` de `serie_localidad.csv` está para eso.
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
