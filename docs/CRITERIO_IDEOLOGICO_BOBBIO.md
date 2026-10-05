# Criterio ideológico para ordenar las fuerzas (Bobbio, 1994)

Orden izquierda-derecha de las familias políticas que usa la pestaña «Swing voters» para decidir el sentido de la flecha.
Datos: `datos/referencia/ubicacion_familias.csv`. Proceso: `scripts/construir_swing.py`.

## Fuente

Bobbio, N. (1994). *Derecha e izquierda. Razones y significados de una distinción política*. Roma: Donzelli (edición española:
Madrid, Taurus, 1995).

**Nota sobre las citas:** el texto de Bobbio no estaba disponible en el entorno de trabajo cuando se escribió este criterio. Las
definiciones que siguen son **paráfrasis sin número de página** de las ideas centrales del libro. Cuando se incorpore el texto,
corresponde completar las páginas y verificar la fidelidad de cada paráfrasis. Como apoyo secundario con página, el artículo de
Valencia Sáiz (pp. 155-171, adjunto en la revista donde se publicó Malamud, 2004) recoge el criterio de Bobbio: la izquierda es
más igualitaria y la derecha menos, entendido como una tendencia y no como una utopía (p. 162).

## Definiciones que da Bobbio (paráfrasis)

- **Izquierda:** se distingue por su orientación hacia la **igualdad**. Considera que muchas desigualdades entre las personas son
  sociales y, por lo tanto, pueden reducirse. La igualdad es una tendencia, no la igualdad de todos en todo.
- **Derecha:** acepta con mayor facilidad las desigualdades, por considerarlas en gran medida naturales o inevitables, y es menos
  proclive a corregirlas.
- **Criterio que separa izquierda de derecha:** la actitud frente a la igualdad.
- **Segundo criterio, la libertad:** distingue dentro de cada polo a los **moderados**, que respetan el orden democrático y
  liberal, de los **extremistas**, que lo rechazan. De combinar ambos criterios resultan cuatro opciones: extrema izquierda
  (igualitaria y antiliberal), centroizquierda (igualitaria y liberal-democrática), centroderecha (inigualitaria y
  liberal-democrática) y extrema derecha (inigualitaria y antiliberal). El **centro** es una posición intermedia entre los polos.

## Cómo se aplica al tablero

1. **Eje principal (igualitarismo).** Cada familia recibe un puntaje de igualitarismo entre 1 y 5: **menor puntaje, más igualitaria,
   más a la izquierda**. El puntaje define el orden estricto de las fuerzas; no hay empates. El sentido de la flecha es el signo
   de la diferencia entre el puntaje de la fuerza que gana ahora y el de la que ganó antes.
2. **Posiciones.** Los puntajes se agrupan en cinco posiciones, de menos de 1,5 a 5: izquierda (menos de 1,5), centroizquierda
   (1,5 a 2,9), centro (2,9 a 3,6), centroderecha (3,6 a 4,5) y derecha radical (4,5 o más, reservada a quien muestre además
   rasgos antiliberales).
3. **Eje secundario (libertad).** Solo La Libertad Avanza tiene evidencia de rasgos antiliberales («tintes autoritarios hacia las
   instituciones democráticas»), por lo que es la única que cumple la definición de extrema derecha de Bobbio. Para las demás no
   hay evidencia de rechazo del orden democrático en las fuentes consultadas.
4. **Qué está respaldado y qué no.** La **posición** de cada familia se apoya en las fuentes citadas cuando estas dan una etiqueta.
   El **puntaje fino** dentro de una posición (por ejemplo, Socialismo 2,0 frente a Kirchnerismo 2,3) es una **codificación de
   investigación** y puede revisarse. La columna de confianza lo indica.

## Escala vigente

| Posición | Puntaje | Familia | Eje de libertad | Confianza | Respaldo en las fuentes |
|---|---:|---|---|---|---|
| Izquierda | 1.0 | Izquierda | sin evidencia de rechazo al orden democrático | media | Murillo, Rubio y Mangonnet (2016: 16): bloque «Izquierda»; Murillo y Oliveros (2024: 164 n. 6, 169, 182) |
| Centroizquierda | 2.0 | Socialismo | democrática y liberal | media | Murillo, Rubio y Mangonnet (2016: 16, 19): bloque PS-GEN / Frente Progresista, sin etiqueta ideológica propia |
| Centroizquierda | 2.2 | Centroizquierda no peronista | democrática y liberal | baja | Sin etiqueta explícita en las fuentes extraídas (Proyecto Sur y fuerzas afines) |
| Centroizquierda | 2.3 | Kirchnerismo | democrática y liberal | alta | Murillo y Oliveros (2024: 170): el kirchnerismo reconfigura el polo peronista «hacia la centroizquierda, aunque aún en alianza con los sectores más conservadores» |
| Centroizquierda | 2.6 | Centro progresista no peronista | democrática y liberal | media | Malamud (2004: 145): el ARI sale de la UCR «por izquierda»; Scaramella (2025: 104): la Coalición Cívica es de «matriz liberal y reformista» |
| Centro | 3.0 | Union Civica Radical | democrática y liberal | media | Scaramella (2025: 104): «partido de tipo catch-all, históricamente federal» |
| Centro | 3.3 | Peronismo Federal | democrática y liberal | media | Scaramella (2025: 104, 115): peronismo no kirchnerista, facciones provinciales opositoras al gobierno nacional; Murillo y Oliveros (2024: 166, 170): «peronismo disidente» y sectores más conservadores |
| Centroderecha | 4.0 | Cambiemos | democrática y liberal | alta | Scaramella (2025: 104): PRO de «orientación centroderecha y corte liberal-republicano»; Murillo, Rubio y Mangonnet (2016: 12); Murillo y Oliveros (2024: 170) |
| Centroderecha | 4.3 | Centroderecha liberal | democrática y liberal | media | Malamud (2004: 145): Recrear sale de la UCR «por derecha»; Scaramella (2025: 104): orientación liberal |
| Derecha radical | 4.7 | Derecha nacionalista | sin evidencia | baja | Sin etiqueta explícita en las fuentes extraídas |
| Derecha radical | 4.8 | Derecha libertaria | sin evidencia | baja | Fuerzas libertarias anteriores a 2023 (Unite, 2019); ver docs/CRITERIO_DERECHA_LIBERTARIA.md |
| Derecha radical | 5.0 | La Libertad Avanza | con tintes autoritarios hacia las instituciones democráticas | alta | Murillo y Oliveros (2024: 161-163): «extrema derecha» y «derecha radical global», ultraliberal en lo económico y conservadora en lo social «con tintes autoritarios»; (2024: 171, 173): actitudes autoritarias y menor compromiso con la democracia |

## Sensibilidad

El sentido de un cambio solo depende del puntaje fino cuando las dos fuerzas están en la misma posición. Esos casos se informan en
la pestaña (columna «Cambios dentro de una misma posición») y en `datos/procesados/swing_resumen.csv`:

| Comparación | Cambios de ganador | Dentro de la misma posición |
|---|---:|---:|
| 2003-2007 | 316 | 12 |
| 2007-2011 | 319 | 169 |
| 2011-2015 | 389 | 1 |
| 2015-2019 | 66 | 0 |
| 2019-2023 | 471 | 0 |

La comparación 2007-2011 es la más sensible: 169 de 319 cambios ocurren entre fuerzas de la centroizquierda (Centro progresista,
Socialismo y Kirchnerismo). Con la escala anterior, que ordenaba a esas fuerzas de otra manera, 29 circuitos de 2007-2011 tenían
flecha a la derecha (Centro progresista → Kirchnerismo) y ahora tienen flecha a la izquierda.
