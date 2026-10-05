# Provisorio y definitivo: en qué difieren y por qué usamos el provisorio

## Los dos recuentos

En Argentina conviven dos conteos de cada elección, y no son lo mismo:

**El recuento provisorio** se difunde la noche de la elección. Lo hace una
empresa contratada a partir de los telegramas que envían las mesas. Es
rápido, es informativo y **no tiene valor legal**.

**El escrutinio definitivo** lo realiza la Justicia Nacional Electoral días
después, abriendo las urnas y cotejando actas. Resuelve mesas impugnadas,
corrige errores de transcripción y suma los votos de mesas que el provisorio
no alcanzó a contar. **Es el resultado válido de la elección** según el
Código Electoral Nacional.

## Cuánto difieren, medido

No es una diferencia teórica. La medimos en los casos donde disponemos de
ambos para Santa Fe:

### PASO 2023 — definitivo (JNE) contra provisorio (DINE)

| Agrupación | Definitivo | Provisorio | Diferencia |
|---|---:|---:|---:|
| La Libertad Avanza | 661.659 | 646.315 | −15.344 (−2,3 %) |
| Juntos por el Cambio | 591.233 | 579.867 | −11.366 (−1,9 %) |
| Unión por la Patria | 394.908 | 386.865 | −8.043 (−2,0 %) |
| Hacemos por Nuestro País | 69.149 | 67.563 | −1.586 (−2,3 %) |

### General 2023 — definitivo (JNE) contra provisorio (DINE)

Brecha total en las principales fuerzas: **−18.456 votos (−0,90 %)**.

### General 2003 — definitivo (Atlas) contra provisorio (Atlas)

| Fórmula | Definitivo | Provisorio | Diferencia |
|---|---:|---:|---:|
| Menem-Romero | 425.886 | 437.667 | +11.781 |
| Carrió-Gutiérrez | 424.085 | 434.526 | +10.441 |
| López Murphy-Gómez Diez | 292.124 | 297.316 | +5.192 |
| Kirchner-Scioli | 271.591 | 275.561 | +3.970 |

Brecha en las cinco principales: **+36.078 votos (+2,32 %)**.

### La conclusión que importa

**El signo de la diferencia no es constante.** En 2023 el provisorio queda
por debajo del definitivo; en 2003 queda por encima. No hay un sesgo
sistemático que se pueda corregir con un factor: cada elección tiene su
propia discrepancia, en magnitud y en dirección.

De ahí se sigue la regla operativa del proyecto: **nunca mezclar ambos
recuentos en un mismo cálculo**. Las tablas llevan una columna
`recuento_tipo` justamente para impedirlo.

El orden de magnitud —en torno al 2 %— es menor que las variaciones
políticas que analizamos, que se mueven en decenas de puntos. No invalida el
análisis, pero debe estar declarado.

## Por qué usamos el provisorio

Por una razón simple: **para el nivel de desagregación que esta
investigación necesita, el definitivo no está publicado.**

| Nivel | Escrutinio definitivo | Recuento provisorio |
|---|---|---|
| Provincia | Disponible | Disponible |
| Departamento | **No publicado** | Disponible |
| Circuito | **No publicado** | Disponible |
| Mesa | **No publicado** | Disponible |

El objeto de este trabajo es el comportamiento del voto a escala
sub-provincial: mapas por circuito, contrastes entre zonas rurales y
urbanas. A nivel provincial el definitivo alcanza, y es el que usamos. Por
debajo de eso **no existe alternativa**.

Elegir el provisorio no fue una decisión metodológica: fue la única opción
disponible.

## Esto es una falla institucional, no nuestra

Conviene dejarlo asentado con precisión, porque es un punto que un lector
podría leer como descuido del investigador.

Las presidenciales de 2023 se celebraron el 13 de agosto, el 22 de octubre y
el 19 de noviembre. **A septiembre de 2026, más de tres años después, los
organismos responsables no han publicado el escrutinio definitivo en formato
desagregado.**

Lo verificamos por tres vías independientes:

1. Los archivos por mesa de la DINE **declaran su propia condición**: la
   columna `recuento_tipo` dice `PROVISORIO` en las 266.624 filas de la PASO
   2023 de Santa Fe. Que esa columna exista indica que el sistema contempla
   una variante `DEFINITIVO` que no se publica.
2. La API oficial solo admite `tipoRecuento=1`, Recuento Provisional. No
   expone el definitivo en ninguna consulta.
3. La diferencia entre ambos es material, como muestran las tablas de arriba.

El Código Electoral Nacional es inequívoco: el escrutinio definitivo es el
acto que establece el resultado válido. De ello se sigue que **el Estado
argentino publica de forma desagregada, accesible y reutilizable el dato que
no tiene valor legal, y reserva el que sí lo tiene a un agregado provincial**
consultable de a una zona por vez.

Esto invierte el orden de prioridades esperable de un sistema democrático. La
transparencia electoral no se agota en informar rápido la noche de la
elección: exige que el resultado definitivo quede disponible de forma
desagregada, verificable y en formatos abiertos, en un plazo razonable. Tres
años no admite justificación técnica.

El costo recae sobre quien investiga. Cualquier análisis del comportamiento
electoral de 2023 a escala de circuito —académico, periodístico o de control
ciudadano— **está forzado a trabajar sobre datos sin valor legal, o a no
hacerse.**

## Qué haríamos si se publicara

La base está preparada. Los archivos por mesa se procesan con
`scripts/agregar_mesa_a_circuito.py` y el esquema no cambiaría: bastaría
volver a correr los scripts sobre los archivos nuevos. La limitación es de
la fuente, no del diseño.

## Alcance de esta afirmación

Verificamos que el definitivo desagregado **no está publicado en los canales
que consultamos**: la API de la DINE, su descarga masiva y el portal de datos
abiertos. No podemos afirmar que no exista en ningún lado —por ejemplo, en
un expediente de la Cámara Nacional Electoral—. Un pedido formal de acceso a
la información pública daría una respuesta por escrito, que sería la prueba
más sólida.
