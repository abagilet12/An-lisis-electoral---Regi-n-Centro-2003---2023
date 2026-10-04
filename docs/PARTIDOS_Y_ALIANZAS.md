# Partidos y alianzas en las elecciones presidenciales, 2003-2023

Primera etapa del trabajo sobre etiquetas partidarias: quiénes fueron los tres
primeros en cada instancia, con el nombre **tal cual lo publica cada fuente**, y
de qué partidos estaba compuesta la alianza que ganó.

Datos en `datos/referencia/top3_por_eleccion.csv` y
`datos/referencia/composicion_alianzas.csv`. Se regeneran con
`scripts/construir_top3_y_alianzas.py`.

## 1. Fuentes y qué se pudo verificar

| Fuente | Qué aporta | Estado |
|---|---|---|
| DINE, Excel por elección (argentina.gob.ar/dine) | Resultados definitivos 2003-2019, nacional y por distrito. **Para 2003, 2007 y 2011 el encabezado trae la lista de partidos de cada alianza.** | Descargado y leído |
| DINE, CSV de mesas 2023 y API | Generales 2023 (provisorio) y país en PASO y balotaje 2023 | Descargado y leído |
| DINE, registro de partidos (UEEDA), cierre 30/09/2026 y su historización desde junio de 2018 | Nombre legal, sigla, fecha de reconocimiento y vigencia de cada partido. **No informa alianzas.** | Aportado por el equipo; leído (sección 7) |
| Base propia (`serie_homologada.csv`) | Santa Fe, doce instancias, recuento provisorio | Leída |
| Cámara Nacional Electoral (electoral.gob.ar) | Actas constitutivas y plataformas 2023 | Accesible, pero los PDF nacionales están **escaneados** sin texto y las actas de Santa Fe son distritales |
| CNE, registro histórico de alianzas (old.pjn.gov.ar) | Alianzas reconocidas 2015 en adelante | **Bloqueado** desde este entorno |
| Prensa y Wikipedia | Composición de Cambiemos, Frente de Todos, etc. | **Bloqueado** desde este entorno |

**Consecuencia:** la composición de las alianzas está verificada contra fuente
oficial para 2003, 2007 y 2011. Para 2015, 2019 y 2023 los nombres de las alianzas
sí están verificados (DINE), pero **la lista de partidos integrantes queda
pendiente** (sección 5). No la completé de memoria en el CSV para no mezclar dato
verificado con dato supuesto.

## 2. Un hallazgo que condiciona todo lo demás: la etiqueta no es el partido

Lo que figura en la boleta y en las bases es el nombre de la **alianza o frente**,
no el de un partido. Los Excel oficiales lo muestran en el encabezado:

- **2003: el Partido Justicialista aparece en tres alianzas distintas que compiten
  entre sí**: Frente por la Lealtad (Menem), Frente para la Victoria (Kirchner) y
  Frente Movimiento Popular (Rodríguez Saá). Una clasificación "peronismo" por
  etiqueta de partido no distingue nada; la unidad es la alianza.
- **«Frente para la Victoria» es el nombre de una alianza en 2003, 2007, 2011 y
  2015, con integrantes que cambian.** En 2003 son 17 partidos (la mayoría
  provinciales); en 2007 son 7, incluidos Frente Grande, Libres del Sur y el
  Frente Cívico para la Concertación Plural; en 2011 son 11.
- **«Coalición Cívica» en 2007 incluye al Partido Socialista** (Orden Nacional),
  con la fórmula Carrió-Giustiniani. En 2011 el Socialista ya está en otra alianza,
  el Frente Amplio Progresista, junto con GEN. Es el dato oficial detrás del
  problema que la base ya marcaba para el socialismo santafesino.
- **Una misma sigla cubre alianzas distintas:** "UNA" es la Concertación para una
  Nación Avanzada (Lavagna, 2007: UCR + MID + Confederación Concertación) y también
  Unidos por una Nueva Alternativa (Massa, 2015). No son continuas.
- **El nombre oficial a veces es más largo que el de la boleta.** En 2003 la
  alianza de Menem figura como «Frente por la Lealtad - Unión del Centro
  Democrático» en el resultado y como «Frente por la Lealtad» en el encabezado.

## 3. Los tres primeros, Santa Fe

Porcentaje sobre votos positivos. Etiqueta tal cual la fuente indicada.

| Elección | 1.º | 2.º | 3.º | Fuente de la fila |
|---|---|---|---|---|
| 2003 General | Alianza Frente por la Lealtad - Unión del Centro Democrático (25,26 %) | Alianza Afirmación para una República Igualitaria (25,16 %) | Alianza Movimiento Federal para Recrear el Crecimiento (17,33 %) | DINE, definitivo |
| 2007 General | Alianza Frente para la Victoria (35,5 %) | Alianza Confederación Coalición Cívica (34,08 %) | Alianza Concertación para una Nación Avanzada (16,55 %) | DINE, definitivo |
| 2011 PASO | Alianza Frente para la Victoria (37,91 %) | Alianza Frente Amplio Progresista (32,8 %) | Alianza Frente Popular (11,61 %) | DINE, definitivo |
| 2011 General | Alianza Frente para la Victoria (41,96 %) | Alianza Frente Amplio Progresista (39,1 %) | Alianza Unión para el Desarrollo Social (5,71 %) | DINE, definitivo |
| 2015 PASO | ALIANZA FRENTE PARA LA VICTORIA (33,03 %) | ALIANZA CAMBIEMOS (31,97 %) | ALIANZA UNIDOS POR UNA NUEVA ALTERNATIVA (UNA) (22,1 %) | DINE, definitivo |
| 2015 General | ALIANZA CAMBIEMOS (35,29 %) | ALIANZA FRENTE PARA LA VICTORIA (31,77 %) | ALIANZA UNIDOS POR UNA NUEVA ALTERNATIVA (UNA) (24,83 %) | DINE, definitivo |
| 2015 Balotaje | ALIANZA CAMBIEMOS (55,72 %) | ALIANZA FRENTE PARA LA VICTORIA (44,28 %) | — | DINE, definitivo |
| 2019 PASO | FRENTE DE TODOS (44,37 %) | JUNTOS POR EL CAMBIO (34,29 %) | CONSENSO FEDERAL (12,33 %) | Base propia, provisorio |
| 2019 General | JUNTOS POR EL CAMBIO (43,49 %) | FRENTE DE TODOS (42,68 %) | CONSENSO FEDERAL (8,98 %) | DINE, definitivo |
| 2023 PASO | LA LIBERTAD AVANZA (36,49 %) | JUNTOS POR EL CAMBIO (32,74 %) | UNION POR LA PATRIA (21,84 %) | Base propia, provisorio |
| 2023 General | LA LIBERTAD AVANZA (32,48 %) | UNION POR LA PATRIA (29,68 %) | JUNTOS POR EL CAMBIO (26,89 %) | DINE (mesas), provisorio; idéntico a la base |
| 2023 Balotaje | LA LIBERTAD AVANZA (62,82 %) | UNION POR LA PATRIA (37,18 %) | — | Base propia, provisorio |

Notas:

- Los puestos coinciden entre la fuente oficial y la base propia en las doce
  instancias. Los porcentajes difieren en décimas porque la base usa el
  recuento provisorio (ver `docs/PROVISORIO_VS_DEFINITIVO.md`).
- **2003 es la elección más reñida:** Menem supera a Carrió por 1.800 votos en el
  definitivo (425.886 contra 424.085).
- **2019 General en Santa Fe la gana Juntos por el Cambio** (43,49 % contra 42,68 %),
  mientras que en el país ganó el Frente de Todos.
- En los balotajes hay solo dos fuerzas.
- Las PASO 2019 y 2023 y el balotaje 2023 de Santa Fe provienen de la base propia;
  no cargué todavía el definitivo por distrito de esas instancias.

### Diferencias de nombre entre la fuente oficial y la base propia

| Elección | Puesto | Etiqueta oficial (DINE) | Etiqueta en la base propia |
|---|---|---|---|
| 2003 General | 1.º | Alianza Frente por la Lealtad - Unión del Centro Democrático | Al. Frente por la Lealtad |
| 2003 General | 2.º | Alianza Afirmación para una República Igualitaria | Al. Afirm.para una Rep. Igualitaria |
| 2003 General | 3.º | Alianza Movimiento Federal para Recrear el Crecimiento | Al. Mov. Fed. P/Recrear el Crecimiento |
| 2007 General | 2.º | Alianza Confederación Coalición Cívica | Confederación Coalición Cívica |
| 2007 General | 3.º | Alianza Concertación para una Nación Avanzada | Alianza Concertación UNA |
| 2015 Balotaje | 1.º | ALIANZA CAMBIEMOS | CAMBIEMOS |
| 2015 Balotaje | 2.º | ALIANZA FRENTE PARA LA VICTORIA | FRENTE PARA LA VICTORIA |

La base abrevia o altera el nombre en 2003 y 2007, y dice «Alianza Concertación
UNA» donde el nombre oficial es «Alianza Concertación para una Nación Avanzada».
Conviene corregirlo en la base: es justo el tipo de ambigüedad que genera la
confusión con la UNA de 2015.

## 4. Contraste: los tres primeros en el país

| Elección | 1.º | 2.º | 3.º | Recuento |
|---|---|---|---|---|
| 2003 General | Alianza Frente por la Lealtad - Unión del Centro Democrático (24,45 %) | Alianza Frente para la Victoria (22,25 %) | Alianza Movimiento Federal para Recrear el Crecimiento (16,37 %) | definitivo |
| 2007 General | Alianza Frente para la Victoria (45,28 %) | Alianza Confederación Coalición Cívica (23,05 %) | Alianza Concertación para una Nación Avanzada (16,91 %) | definitivo |
| 2011 General | Alianza Frente para la Victoria (54,11 %) | Alianza Frente Amplio Progresista (16,81 %) | Alianza Unión para el Desarrollo Social (11,14 %) | definitivo |
| 2015 PASO | ALIANZA FRENTE PARA LA VICTORIA (38,67 %) | ALIANZA CAMBIEMOS (30,12 %) | ALIANZA UNIDOS POR UNA NUEVA ALTERNATIVA (UNA) (20,57 %) | definitivo |
| 2015 General | ALIANZA FRENTE PARA LA VICTORIA (37,08 %) | ALIANZA CAMBIEMOS (34,15 %) | ALIANZA UNIDOS POR UNA NUEVA ALTERNATIVA (UNA) (21,39 %) | definitivo |
| 2015 Balotaje | ALIANZA CAMBIEMOS (51,34 %) | ALIANZA FRENTE PARA LA VICTORIA (48,66 %) | — | definitivo |
| 2019 PASO | FRENTE DE TODOS (49,49 %) | JUNTOS POR EL CAMBIO (32,94 %) | CONSENSO FEDERAL (8,44 %) | definitivo |
| 2019 General | FRENTE DE TODOS (48,24 %) | JUNTOS POR EL CAMBIO (40,28 %) | CONSENSO FEDERAL (6,15 %) | definitivo |
| 2023 PASO | LA LIBERTAD AVANZA (31,57 %) | JUNTOS POR EL CAMBIO (29,72 %) | UNION POR LA PATRIA (28,66 %) | provisorio |
| 2023 General | UNION POR LA PATRIA (36,69 %) | LA LIBERTAD AVANZA (29,99 %) | JUNTOS POR EL CAMBIO (23,84 %) | provisorio |
| 2023 Balotaje | LA LIBERTAD AVANZA (55,69 %) | UNION POR LA PATRIA (44,31 %) | — | provisorio |

Divergencias entre Santa Fe y el país en quién ganó la primera vuelta o la general:
**2003** (país: Frente por la Lealtad, igual que Santa Fe, pero Kirchner asumió
tras el retiro de Menem del balotaje); **2015 General** (país: Frente para la
Victoria; Santa Fe: Cambiemos); **2019 General** (país: Frente de Todos; Santa Fe:
Juntos por el Cambio); **2023 General** (país: Unión por la Patria; Santa Fe: La
Libertad Avanza).

Las PASO y el balotaje 2023 nacionales vienen de la API (provisorio): los
definitivos difieren en décimas.

## 5. La alianza ganadora y su composición

Ganadora en Santa Fe y en el país, instancia por instancia. Composición según el
encabezado de los Excel oficiales de la DINE, columna «partido integrante»
(`composicion_alianzas.csv`). Las etiquetas entre paréntesis son las que el
Excel pone para indicar el distrito del partido.

| Elección | Ganó en Santa Fe | Ganó en el país | Composición verificada |
|---|---|---|---|
| 2003 General | Frente por la Lealtad - UCD | Frente por la Lealtad - UCD | **Sí (DINE).** 15 partidos: Justicialista, Conservador Popular, Cambio con Justicia Social, Por un Nuevo Jujuy, Demócrata Conservador, Movimiento Popular Unido, Movimiento Popular Cordobés, Todos por los Jubilados, Movimiento de Acción Vecinal, Opción Federal, Encuentro Popular, Reconquista, De la Generación Intermedia, Frente de los Jubilados, Movimiento por la Justicia Social. La Unión del Centro Democrático figura en el nombre del resultado. |
| 2007 General | Frente para la Victoria | Frente para la Victoria | **Sí (DINE).** 7: Justicialista, Frente Grande, Movimiento Libres del Sur, Intransigente, Conservador Popular, De la Victoria, Confederación Frente Cívico para la Concertación Plural. |
| 2011 PASO | Frente para la Victoria | Frente para la Victoria | **Sí (DINE).** 11, entre ellos Justicialista, Frente Grande, Kolina, Intransigente, Solidario, De la Victoria, Humanista, Comunista y Conservador Popular. |
| 2011 General | Frente para la Victoria | Frente para la Victoria | Idem PASO 2011. |
| 2015 PASO | Frente para la Victoria | Frente para la Victoria | Nombre verificado; **integrantes pendientes**. |
| 2015 General | **Cambiemos** | Frente para la Victoria | Nombre verificado; **integrantes pendientes**. |
| 2015 Balotaje | Cambiemos | Cambiemos | Nombre verificado; **integrantes pendientes**. |
| 2019 PASO | Frente de Todos | Frente de Todos | Nombre verificado; **pendiente**. |
| 2019 General | **Juntos por el Cambio** | Frente de Todos | Nombre verificado; **pendiente**. |
| 2023 PASO | La Libertad Avanza | La Libertad Avanza | Nombre verificado; **pendiente**. |
| 2023 General | La Libertad Avanza | **Unión por la Patria** | Nombre verificado; **pendiente**. |
| 2023 Balotaje | La Libertad Avanza | La Libertad Avanza | Nombre verificado; **pendiente**. |

Las alianzas que quedaron segundas o terceras en 2003-2011 también están
completas en el CSV (por ejemplo, el Frente Amplio Progresista de 2011 es
Socialista + GEN; la Concertación de 2007 es UCR + MID + Confederación
Concertación para una Sociedad Justa; la Afirmación para una República
Igualitaria de 2003 es Afirmación para una República de Iguales + Intransigente).

**Para completar 2015-2023 se necesita una de estas dos cosas:** las actas
constitutivas nacionales de la CNE (hay que abrirlas desde fuera de este entorno o
pasarme los PDF) o la hoja de alianzas del Registro de la CNE. Con cualquiera de
las dos lo cierro con fuente oficial.

## 6. Las dos consideraciones para mostrar las etiquetas (decididas)

1. **Alianza, no partido.** Cada elección muestra el **nombre oficial de la alianza o
   frente** tal como figura en la boleta, y debe poder abrirse en los partidos que
   lo integran. La etiqueta de boleta no es el partido (sección 2).
2. **Cambios de nombre en el tiempo.** Cada etiqueta se muestra con el nombre que
   tuvo en esa elección y con el vínculo a la anterior, **sin agruparlas bajo un
   nombre único**. Por ejemplo, Frente para la Victoria (2003-2015), Frente de Todos
   (2019) y Unión por la Patria (2023) se muestran como tres etiquetas encadenadas.

Dos casos que esta regla evita confundir: la UNA de 2007 y la UNA de 2015 no son
continuas, y en 2003 el mismo partido (el Justicialista) integra tres alianzas que
compiten entre sí.

## 7. Registro de partidos de la DINE (UEEDA, cierre 30/09/2026)

Los dos archivos aportados están en `datos/crudos/dine_registro_partidos/`:
partidos vigentes hoy (737: 44 nacionales y 693 de distrito, 45 de ellos en Santa
Fe) y su historización desde el cierre del 15/06/2018 (1.265 registros, de los
cuales 528 corresponden a partidos que ya no figuran como vigentes).

**Qué sirve y qué no:**

- **No contiene alianzas ni frentes.** Es el padrón de partidos, de modo que no
  cierra la composición de 2015-2023.
- **Sirve para fijar el nombre legal y la sigla** de cada partido integrante y para
  saber si sigue vigente. El cruce con los integrantes de 2003-2011 está en
  `datos/referencia/partidos_integrantes_vs_registro.csv` (se regenera con
  `scripts/cruzar_registro_partidos.py`).
- **Cobertura del cruce (198 integrantes):** 70 coinciden con un partido de orden
  nacional (10 de ellos marcados «probable, revisar» por nombre genérico o dudoso,
  como «Popular», «Autonomista» o «Unión Popular»), 81 son partidos provinciales de
  otro distrito que no se evaluaron, y 47 no figuran en el registro. Estos últimos
  pueden haberse extinguido antes de 2018: el registro no lo permite saber.
- **Cuidado con `fecha_reconocimiento`:** en varios casos es la de un nuevo
  reconocimiento y no la de fundación (la Unión del Centro Democrático figura en 2023).

**Lo que el registro sí deja ver de 2015-2023**, como dato de contexto y no de
composición de alianzas:

| Partido (nombre legal) | Reconocimiento nacional | Estado |
|---|---|---|
| Frente Renovador | 12/06/2019 | vigente |
| Unite por la Libertad y la Dignidad | 12/06/2019 | baja, último cierre 31/10/2023 |
| La Libertad Avanza | 20/11/2024 | vigente |
| Hacemos | 24/06/2025 | vigente |
| Compromiso Federal | 13/05/2016 | vigente |
| Kolina | 13/06/2011 | vigente |
| Nuevo Encuentro por la Democracia y la Equidad | 21/08/2014 | vigente |
| Patria Grande | 14/04/2023 | vigente |
| Partido Fe | 06/02/2015 | vigente |

Conviene leer esa tabla con una advertencia: **un partido con reconocimiento
posterior a una elección no pudo ser la etiqueta de esa elección.** «La Libertad
Avanza» y «Hacemos por Nuestro País» son nombres de alianza en 2023, mientras que
los partidos registrados con nombres iguales o muy parecidos («La Libertad Avanza», «Hacemos») se reconocieron en 2024 y 2025. La etiqueta
de la boleta y el partido registrado coinciden en el nombre pero no son la misma
unidad, que es lo que la sección 2 ya advertía.

**Lo que haría falta para cerrar 2015-2023:** el registro de alianzas o las actas
constitutivas de la Cámara Nacional Electoral, que la DINE publica por separado de
este padrón. Si encontrás en la DINE un archivo de «alianzas» o «frentes electorales»
con la misma estructura (UEEDA), lo cargo con el mismo procedimiento.

