# Metodología del tablero

Describe cómo se hizo cada gráfico y cada tabla de `salida/voto_santafesino.html`: la base y sus fuentes, los métodos (de quién
vienen y qué decidimos nosotros), un resumen por pestaña y una propuesta de hallazgos con su conexión teórica.

Convención: **[Autor]** marca lo que viene de la literatura; **[Equipo]** marca una decisión de investigación, editable y
documentada. Las cifras citadas son las que muestra el tablero (recuento provisorio, porcentaje sobre votos positivos salvo
indicación).

---

## 1. Base de datos y fuentes

**Alcance.** Categoría Presidente y Vice, Santa Fe (distrito 21), 19 departamentos, 12 instancias entre 2003 y 2023 (6 generales,
4 PASO —2011, 2015, 2019 y 2023— y 2 balotajes —2015 y 2023—). Marco: `docs/00-encuadre.md`.

**Fuentes.**

| Uso | Fuente | Recuento |
|---|---|---|
| Resultados por mesa → circuito, 2003-2019 | PoliticaArgentina/data_warehouse (origen: Atlas Electoral de Andy Tow) | Provisorio |
| Resultados por mesa → circuito, 2023 | Dirección Nacional Electoral (DINE), portal de datos abiertos | Provisorio |
| Control provincial | Excel de la DINE por distrito (generales 2003-2019, PASO 2011 y 2015, balotaje 2015) y Consulta de Escrutinio por Zona de la Justicia Nacional Electoral (2023) | Definitivo |
| Circuitos por localidad (30 localidades) | Archivos «Votos por Localidad», 2007-2023 | Provisorio |
| Cartografía de circuitos | Franco Galeano (CC BY 4.0); capas 2003-2019 y 2023 reconstruidas | — |
| Población por localidad | Censo 2022, INDEC, base por radio censal | — |
| Fórmulas y partidos | Registro de candidaturas y registro de partidos (UEEDA) de la DINE | Oficial |

**Construcción** (`docs/CRITERIO_BASE_DE_DATOS.md`). Crudos intocables → CSV ordenados (una fila por observación) → un `.xlsx` por
elección. Se agrega de mesa a circuito, a departamento y a provincia; el **circuito es la unidad de referencia** (la menor con
identidad territorial estable). Reglas: solo votos absolutos (los porcentajes se calculan al analizar, con el denominador
explícito); código de circuito como texto con ceros; cada fila declara `fuente` y `recuento_tipo`; nunca se mezclan recuentos.

**Controles.** Las agrupaciones suman los positivos; positivos + blancos + nulos + impugnados + recurridos = votantes; la
participación calculada coincide con la declarada; en PASO las listas suman su agrupación. Cobertura de votos mapeables:
más del 99,8 % en las doce instancias.

**Recuento provisorio** (`docs/PROVISORIO_VS_DEFINITIVO.md`). El escrutinio definitivo desagregado no está publicado: por debajo del
total provincial solo existe el provisorio. La diferencia ronda el 2 % y su signo no es constante (2023: el provisorio queda por
debajo; 2003: por encima), de modo que no se corrige con un factor. **[Equipo]** el nivel provincial usa el definitivo cuando
existe; circuito, departamento y localidad usan el provisorio; ambos no se mezclan en un mismo cálculo.

---

## 2. Métodos: autores y decisiones propias

| Procedimiento | **[Autor]** | **[Equipo]** |
|---|---|---|
| Combinar análisis estadístico y cartográfico, en un marco multinivel | Scaramella (2025: 109, 122-125) | Aplicado a la categoría Presidente en Santa Fe; unidad = circuito. |
| Elecciones «definitivas» (las que definieron presidente) | Mayoría especial: más del 45 % o más del 40 % con 10 puntos de diferencia; si no, balotaje (Scaramella, 2025: 109) | Generales 2003, 2007, 2011 y 2019 y balotajes 2015 y 2023. Las PASO no entran en comparaciones: no son comparables con las generales. |
| Fuerzas políticas como **etiquetas focales** | Escolar (2011: 285, n. 38, a partir de Cox) | 82 etiquetas → 52 fuerzas → 13 familias, en `homologacion_agrupaciones.csv` (editable). FPV, Frente de Todos y UxP son una familia; la UCR no se imputa retroactivamente a Cambiemos; el Socialismo se mantiene propio; 2007 se clasifica por fórmula. |
| Derecha libertaria y La Libertad Avanza | Murillo y Oliveros (2024: 161-163, 171, 173) | «Derecha libertaria» solo hasta 2019 (Unite); «La Libertad Avanza» desde 2023. La continuidad queda como pregunta, no como supuesto. Efecto: la volatilidad 2019-2023 suma ambas. |
| Denominadores | Convención de los organismos electorales | Comparar fuerzas: % sobre positivos. Además, % sobre válidos y sobre emitidos. Participación sobre padrón; blanco y nulo sobre votantes; ausentismo = 100 − participación. |
| **Volatilidad** (índice de Pedersen) | Pedersen (1979): cambio neto total del sistema de partidos entre dos elecciones; ½ Σ \|Δ %\| | Se aplica a los % sobre positivos de cada familia política (más «Otras fuerzas»). Solo entre generales consecutivas; en el resumen, extremos 2003-2023 y promedio simple de los cinco pares. |
| **Swing voters** | Mayer (2008: 2, 12-13): distingue swing voter de *party switcher* | Aplicado a territorios: un circuito «cambia» si cambia su ganador (familia más votada). Enlace histórico entre circuitos; sin equivalente = punto gris, no cuenta como cambio. Los datos agregados no separan voto cruzado, abstención ni cambios de oferta (inferencia ecológica). |
| **Escala izquierda-derecha** (sentido de la flecha) | Bobbio (1994): izquierda y derecha se distinguen por la actitud frente a la igualdad; la libertad separa moderados de extremos | Puntaje de igualitarismo 1-5 por familia, cinco posiciones, eje de libertad (solo La Libertad Avanza con rasgos antiliberales). Posición respaldada en Malamud (2004: 145), Scaramella (2025: 104, 115), Murillo, Rubio y Mangonnet (2016) y Murillo y Oliveros (2024); **el puntaje fino es codificación del equipo** y se informa su sensibilidad. |
| **Tamaño del lugar** | Censo 2022 (INDEC). La lógica de leer el cambio según el tamaño del lugar se tomó de un análisis de Schteingart sobre Brasil, cuyo texto no se pudo consultar | Escala de 5 categorías (rural ≤ 2.000; pueblo 2.001-5.000; ciudad pequeña 5.001-10.000; intermedia 10.001-50.000; grande desde 50.001). Cada circuito se asigna al gobierno local que aporta más población dentro de su polígono; corrección por padrón (circuito 04250). Rosario (1.030.069) se incluye en «grande». |
| Color | — | Un color por familia (`docs/CRITERIOS_COLOR.md`). Tamaño del lugar: rampa ordinal de un solo tono (extremo claro con contraste ≥ 2:1) más forma de marcador. |

---

## 3. Gráficos y tablas por pestaña

Cada gráfico y tabla lleva debajo su epígrafe de fuentes («Elaboración propia a partir de…»; `scripts/plantillas/epigrafes.js`).

### Objetivos, método y base de datos
Solo texto (sin gráficos ni tablas de datos): los cinco objetivos; el marco de referencia (gobernanza electoral multinivel,
territorialización y nacionalización; Scaramella, 2025); la construcción de la base; y las advertencias (recuento provisorio,
qué es una «fuerza política», PASO frente a generales, fuentes).

### Evolución del voto

| Elemento | Qué muestra | Cómo se construye y qué cuidar |
|---|---|---|
| Mapa de la serie por circuito | Las 12 instancias sobre los circuitos, con deslizador. Modo «fuerza ganadora» o «intensidad por fuerza». Un clic abre la ficha histórica del circuito (ganador y segundo en las 12 elecciones) | Color = familia más votada; intensidad = tinte de la familia, proporcional al máximo de esa elección. Capa de circuitos de cada año; 43 circuitos sin polígono no se dibujan pero suman en departamento y provincia. Tres líneas de interpretación con cifras verificables |
| El voto departamento por departamento | Los 19 departamentos, con los mismos dos modos | Departamento = suma de circuitos. El código departamental de las capas 2003-2019 se tradujo por nombre (había 4 a 11 departamentos mal pintados) |
| Comparación de las elecciones definitivas | Seis mapas por circuito en paralelo (generales 2003, 2007, 2011, 2019; balotajes 2015 y 2023); modo ganador, cantidad de votos o variación de votos | Sin deslizador, para comparar configuraciones. En «votos», votos positivos del circuito en cinco tramos de límites fijos (hasta 1.000; 1.001 a 5.000; 5.001 a 10.000; 10.001 a 50.000; más de 50.000), iguales en las seis elecciones, con una rampa de un solo tono. En «variación», cambio porcentual de los votos positivos de cada circuito respecto del mapa anterior (2007 respecto de 2003, etc.), en cinco tramos simétricos (baja o sube 20 % o más; entre 5 y 20 %; menos de 5 %), con el enlace histórico entre circuitos: si un circuito se subdividió, se compara la suma de los circuitos resultantes con el original. Los circuitos sin equivalente (16 a 20 por elección) se rayan. Tres comparaciones cruzan general y balotaje, y un trazado modificado puede reflejar cambio de territorio y no de votos |

### Swing voters

| Elemento | Qué muestra | Cómo se construye y qué cuidar |
|---|---|---|
| Mapa con flechas y vista ampliada | Por circuito, entre pares de elecciones definitivas: flecha a la derecha o a la izquierda si cambió el ganador, «=» si hubo continuidad, punto gris si no hay equivalente | Sentido según la escala de Bobbio; color = fuerza que gana ahora. Flecha de línea con punta abierta, sin relleno, para que las superpuestas se distingan. Tamaño de la marca ajustado a la cantidad de circuitos |
| Resumen de la comparación elegida | Circuitos que continuaron, cambiaron a la derecha o a la izquierda, y los cambios más frecuentes | Ej. 2019-2023: 471 de 522 cambiaron (90,2 %); 470 a la derecha |
| Las cinco comparaciones (mosaico y tabla) | 2003-2007, 2007-2011, 2011-2015, 2015-2019, 2019-2023: circuitos comparables, continuidad, dirección, % que cambió, cambios dentro de una misma posición | Tres comparaciones cruzan general y balotaje: el cambio incluye el efecto de la oferta. 2007-2011 es la más sensible a la escala (169 de 319 cambios ocurren dentro de la misma posición) |
| El cambio según el tamaño del lugar | % de circuitos comparables que cambiaron, por categoría | Una proporción parecida entre categorías indica que el cambio no depende del tamaño del lugar |
| Escala izquierda-derecha (desplegable) | Posición, puntaje y familia | Fuente y confianza por familia en `datos/referencia/ubicacion_familias.csv` |

### Análisis estadístico

| Elemento | Qué muestra | Cómo se construye y qué cuidar |
|---|---|---|
| La serie en cifras | % de votos positivos de cada familia en cada general, más participación y blancos y nulos; por provincia o departamento | El guion no es cero: indica que la fuerza no se presentó |
| Tabla por elección | Resultado completo de una instancia por etiqueta oficial: votos, % positivos, % válidos, % emitidos; electores, votantes, participación, mesas y margen entre el primero y el segundo | Los tres denominadores no son intercambiables |
| Composición por departamento | Barras apiladas del voto positivo de cada departamento, ordenadas por padrón o por fuerza ganadora | Una elección a la vez |
| Volatilidad electoral | Índice de Pedersen entre generales consecutivas (29, 49, 53, 23 y 33 para la provincia) | Siempre entre generales; el ámbito sí se aplica. Fuerzas agrupadas por familia |
| Desafección | Participación (sobre el padrón) y voto en blanco y nulo (sobre los votantes), un punto por año | Con «Todas», cada punto es el promedio simple de las instancias de ese año (2015 y 2023: tres; 2011 y 2019: dos; 2003 y 2007: una); con «Solo generales», la general. Sin etiquetas finales: los valores se leen al pasar el puntero. Dos bandas con escalas propias: una sola escala aplastaría las series de menor magnitud |

### Hallazgos

| Elemento | Qué muestra | Cómo se construye y qué cuidar |
|---|---|---|
| Resumen de 5 números | Volatilidad 2003-2023 (73,1 %; promedio entre consecutivas 37,3 %), partidos por elección (9,3), blancos (1,7 %), nulos (1,2 %) y ausentismo (22,9 %) | Seis generales, provincia, recuento provisorio; promedios simples. Una alianza cuenta como un partido |
| Evolución de las fuerzas políticas | Líneas de las tres fuerzas que ganaron la presidencia (Kirchnerismo, Cambiemos / Juntos por el Cambio, La Libertad Avanza), en % positivos o votos | La ausencia de línea indica que la fuerza no se presentó. Con «todas», PASO y balotajes se intercalan y la serie deja de ser homogénea |
| El voto según el tamaño del lugar (gráfico, tabla y listado de localidades) | Una línea por categoría con el % de la fuerza elegida sobre los positivos del conjunto de localidades de la categoría; tabla con los mismos valores, votos asignados y cobertura (99,8-100 %) | Eje vertical ajustado al rango de la fuerza (no parte de cero). 365 localidades. Control: reproduce 149 de 150 circuitos del nomenclador a mano; diferencia media de 0,6 % contra las 30 localidades con resultados propios |

### Elecciones

| Elemento | Qué muestra | Cómo se construye y qué cuidar |
|---|---|---|
| Mapa de la ficha | Resultado de una elección por departamento o circuito; un clic selecciona la unidad | El color identifica la familia de cada etiqueta, no su puesto |
| Tabla de resultado | Votos y % positivos por partido (nombre oficial) para la unidad elegida; en el total provincial, columna definitiva de la DINE cuando existe | El recuento por unidad es provisorio |
| Participación, blancos y nulos | Electores, votantes, participación, blancos, nulos e impugnados | Votantes = positivos + blancos + nulos + impugnados, recurridos y comando |

### Partidos

| Elemento | Qué muestra | Cómo se construye y qué cuidar |
|---|---|---|
| Evolución | Barras con el % positivo del partido en las 12 instancias | «—» no es cero; «s/d» indica que solo hay total provincial. Los vínculos entre etiquetas son una ayuda de navegación, no una afirmación de identidad |
| Nombres y resultados | Nombre oficial, votos, % y puesto en cada instancia | Un clic en una fila selecciona la elección del mapa |
| Mapa de intensidad y ranking por departamento | Intensidad del voto del partido y departamentos ordenados | Tinte de la familia del partido, hasta el máximo observado |

---

## 4. Hallazgos sugeridos y conexión teórica

Se formulan como lecturas, no como causas. Las citas de la columna teórica son las que ya están en `docs/REFERENCIAS.md` salvo
indicación.

1. **Alternancia sin fuerza dominante y fin del bipartidismo.** Cuatro fuerzas distintas ganaron las seis generales; los márgenes
   fueron estrechos en 2019 (43,4 % frente a 42,7 %) y 2023 (32,5 % frente a 29,7 %).
   *Teoría:* Malamud (2004) explica la persistencia del bipartidismo hasta 2003; Murillo y Oliveros (2024: 170) recuerdan que
   hasta 2001 había dos coaliciones no ideológicas y que en 2003 cada una presentó tres candidatos. La serie empieza en una
   oferta fragmentada dentro de ambos polos.

2. **Reacomodamiento fuerte y no monótono.** Pedersen: 29, 49, 53, 23 y 33; el máximo (2011-2015) coincide con la caída del
   Socialismo (39,1 % a 4,0 %) y el ascenso de Cambiemos; el mínimo (2015-2019) con la competencia entre dos coaliciones
   (Cambiemos y Kirchnerismo suman 67,1 % y 86,1 %). *Teoría:* etiquetas focales como mecanismo de coordinación (Escolar, 2011);
   el reacomodamiento depende de qué etiqueta se vuelve focal. *Cautela:* tratar Unite y La Libertad Avanza como fuerzas
   distintas eleva la volatilidad 2019-2023.

3. **Cambio territorial casi total en 2023 y estabilidad en 2019.** Cambió el ganador en el 13,1 % de los circuitos entre 2015 y
   2019 y en el 90,2 % entre 2019 y 2023 (470 hacia la derecha; Cambiemos → La Libertad Avanza en 333 y Kirchnerismo → La
   Libertad Avanza en 137); entre 2011 y 2015 cambió el 77,3 %, todo hacia la derecha (Socialismo → Cambiemos, 208). *Teoría:*
   los hitos del encuadre (peso de la región en el triunfo de 2015 y en el de 2023); Mayer (2008) para el alcance del concepto;
   Scaramella (2025: 122-123) para el alineamiento vertical con el gobierno nacional y los clivajes geográficos del Litoral.
   *Cautela:* tres comparaciones cruzan general con balotaje; el sentido de 2007-2011 depende del puntaje fino.

4. **Territorio heterogéneo en generales y homogéneo en balotajes.** En 2023 el Kirchnerismo conserva Rosario, Constitución,
   San Javier y Vera frente a La Libertad Avanza en los otros quince; en los balotajes el polo no kirchnerista gana 18 de 19
   departamentos en 2015 y los 19 en 2023. *Teoría:* configuración fragmentada del poder territorial y desajuste de escalas
   (Scaramella, 2025: 116, 120, 123-125): en 2023 Juntos por el Cambio ganó la gobernación y La Libertad Avanza la presidencia.

5. **El tamaño del lugar cambió de signo.** El Kirchnerismo es más débil en las ciudades grandes en 2003 (13,5 % frente a
   20,7 % en lo rural), el gradiente es nulo o negativo hasta la general de 2015 y pasa a ser positivo desde el balotaje de 2015
   (46,0 % frente a 39,6 %; 2019: 43,5 % frente a 39,6 %; 2023: 32,2 % frente a 25,4 %). Cambiemos hace el
   camino inverso (2019: 50,9 % rural y 41,5 % en ciudad grande) y en 2023 las cinco categorías quedan entre 25,0 % y 27,8 %. La Libertad
   Avanza es más débil en ciudades grandes (29,8 % frente a 37,5 %; balotaje, 60,0 % frente a 68,2 %). La base del progresismo era
   urbana (Centro progresista 2003: 12,5 % rural y 29,5 % ciudad grande; Socialismo 2011: 33,2 % y 42,1 %). Además, 54,6 % de los
   votos positivos de 2023 están en solo 9 localidades. *Teoría:* clivajes geográficos (Scaramella, 2025: 123); para el voto a
   La Libertad Avanza, los textos del plan (Nazareno y Brusco, 2024; Tagina, 2024), que no están en el repositorio. *Cautela:*
   lectura ecológica de localidades, no de personas.

6. **Menor movilización en 2023.** La participación fue la más baja de la serie (73,2 %, frente a 75,4-79,7 % antes), mientras que
   blancos y nulos fueron bajos (2,2 %): la desafección se expresó como ausencia, no como voto en blanco o nulo. *Cautela:*
   el padrón incluye registros no depurados, que inflan el ausentismo.

7. **Oferta que se concentra con reconfiguración de polos.** Compitieron 18 partidos en 2003 y 5 en 2023 (9,3 en promedio), con
   alta volatilidad. *Teoría:* coordinación de electores y élites en etiquetas focales (Escolar, 2011).

---

## 5. Límites y pendientes

- **Recuento provisorio:** por debajo del total provincial no hay definitivo publicado; la brecha ronda el 2 % y cambia de signo.
- **Inferencia ecológica:** todo se mide en circuitos o localidades, no en votantes.
- **Tamaño del lugar:** se usa la población de 2022 para clasificar todas las elecciones, incluida 2003. Cuatro localidades están a menos
  del 1 % de un límite (Frontera, Monte Vera, Nelson y Colonia Aldao); el total del censo por radio queda 0,73 % bajo el oficial.
- **Circuitos:** la cartografía de 2023 y 2025 usa polígonos reconstruidos; 43 circuitos no tienen polígono.
- **Clasificación de familias:** el puntaje fino de la escala y la continuidad FPV-FdT-UxP son decisiones del equipo.
- **Referencias incompletas:** faltan las páginas de Bobbio (1994; hoy son paráfrasis contrastadas con reseñas); el año y el volumen de
  Mayer (2008) se dedujeron; Escolar (2011), Torres (2019), Murillo, Rubio y Mangonnet (2016) y Murillo y Oliveros (2024) tienen datos
  incompletos. El análisis de Schteingart no se pudo consultar.
- **Spearman:** la tabla de tamaño del lugar ya no lo muestra; `tamano_lugar_correlaciones.csv` se sigue generando.

## 6. Lecturas sugeridas fuera de la bibliografía del proyecto

Citadas de memoria y sin páginas: **verificar los datos antes de incorporarlas.**

- Robinson, W. S. (1950). Ecological correlations and the behavior of individuals. *American Sociological Review*, 15(3) — límites de
  la inferencia ecológica.
- Jones, M. P. y Mainwaring, S. (2003). The nationalization of parties and party systems. *Party Politics*, 9(2) — nacionalización:
  comparar Santa Fe con el país (en 2019 gana Juntos por el Cambio en Santa Fe y el Frente de Todos en el país;
  `datos/referencia/top3_por_eleccion.csv`).
- Calvo, E. y Escolar, M. (2005). *La nueva política de partidos en la Argentina*. Prometeo — territorialización de la competencia.
- Gibson, E. L. y Suárez-Cao, J. (2010). Federalized party systems and subnational party competition. *Comparative Politics*, 43(1).
- Indicador adicional: número efectivo de partidos (Laakso y Taagepera, 1979) para medir la fragmentación del hallazgo 7.
