# El voto según el tamaño del lugar

Cobertura: **toda la provincia, 12 instancias (2003-2023), 365 localidades** (gobiernos locales, con su zona rural).

## Escala demográfica

Definida en `datos/referencia/escala_tamano_lugar.csv` (se edita ahí, no en el código):

| Categoría | Habitantes |
|---|---|
| Rural | menos de 2.000 (el valor 2.000 se asigna aquí) |
| Pueblo | 2.001 a 5.000 |
| Ciudad pequeña | 5.001 a 10.000 |
| Ciudad intermedia | 10.001 a 50.000 |
| Ciudad grande | 50.001 a 1.000.000 (Rosario, con 1.030.069, supera el tope y se incluye) |

## Cadena de datos

```
resultados por circuito ──► localidad (cartografía × radios censales) ──► población 2022 ──► categoría ──► voto por familia
```

1. **Resultados:** `datos/procesados/serie_homologada.csv`, nivel `circuito`, con la familia política de cada etiqueta
   (incluye el criterio de `docs/CRITERIO_DERECHA_LIBERTARIA.md`).
2. **Circuito → localidad:** `scripts/asignar_circuitos_a_localidad.py` cruza la cartografía de circuitos de cada elección
   (`datos/geo/circuitos/`) con los radios censales 2022 del INDEC. Cada circuito se asigna al gobierno local que aporta más
   población dentro de su polígono. Resultado: `datos/referencia/circuito_localidad.csv` y
   `datos/referencia/poblacion_gobiernos_locales_censo2022.csv`.
3. **Población:** Censo 2022 (INDEC), población en viviendas particulares por radio censal (3.519.059 en Santa Fe). Queda
   levemente por debajo del total oficial publicado. **Si el equipo tiene la tabla oficial por localidad, reemplazar la
   columna `poblacion_2022` del CSV de gobiernos locales y volver a correr los scripts.**
4. **Agregación y categorías:** `scripts/construir_tamano_lugar.py` suma los circuitos de cada localidad, clasifica y escribe
   `datos/procesados/tamano_lugar.csv`, `datos/procesados/tamano_lugar_correlaciones.csv` y `salida/datos_tamano_lugar.json`.
   `scripts/agregar_tamano_lugar.py` lo inserta en el tablero.

## Controles realizados

| Control | Resultado |
|---|---|
| Votos que no se pueden asignar a una localidad | como máximo 0,17 % por elección |
| El cruce espacial contra el nomenclador circuito→localidad relevado a mano (150 circuitos) | 149 de 150; el desacuerdo (circuito 01345 de 2023, Frontera/Josefina) se corrige con el nomenclador, que prevalece |
| Votos reconstruidos desde circuitos contra la fuente por localidad (30 localidades × 11 elecciones = 330 pares) | diferencia media absoluta de 0,6 %; solo 4 pares superan el 10 % (Frontera 2019, San Carlos Sud 2011 general, Santa Clara de Saguier 2015 general), por diferencias entre las propias fuentes |
| Ningún gobierno local reúne circuitos de más de un departamento | cumplido en las capas 2003, 2011, 2019 y 2023 |
| Circuitos con menos del 90 % de su población en una sola localidad | 7 a 10 por capa |
| Electores 2023 / población de 16+ por localidad | mediana 1,07; la corrección por padrón mueve un circuito (04250, Ricardone → San Lorenzo) |

Chequeo de la población y corrección por padrón del circuito 04250 de 2023: ver `docs/VERIFICACION_POBLACION.md`.

## Resultado de la clasificación

| Categoría | Localidades | % de los votos positivos 2023 (general) |
|---|---:|---:|
| Rural | 198 | 4,5 |
| Pueblo | 73 | 6,6 |
| Ciudad pequeña | 45 | 9,2 |
| Ciudad intermedia | 40 | 25,1 |
| Ciudad grande | 9 | 54,6 |

## Cómo se dibuja el gráfico del tablero

Pestaña «Hallazgos», sección «El voto según el tamaño del lugar» (`dibujarTramos` en `salida/voto_santafesino.html`):

- **Una línea por categoría**, con el porcentaje sobre los votos positivos del conjunto de localidades de la categoría. No se rotulan cifras al final de las líneas: los valores se leen en la tabla de debajo o al pasar el puntero (o con las flechas del teclado) sobre una elección.
- **Identidad de cada categoría:** tono de una rampa ordinal de un solo color (`--accent`, de claro a oscuro según el tamaño; validada: pasos de luminosidad uniformes y extremo claro con contraste ≥ 2:1 contra el fondo) **más** una forma de marcador propia (círculo, cuadrado, rombo, triángulo y cruz). Los marcadores crecen con la categoría y se dibujan de mayor a menor: si dos categorías coinciden en una elección (por ejemplo, Pueblo y Ciudad pequeña de Kirchnerismo en 2003, ambas 19,9 %), se siguen viendo los dos.
- **Etiquetas:** solo el nombre de la categoría, con una línea guía hacia el último punto de la serie. La leyenda repite forma y tono; al pasar o fijar una categoría en la leyenda, las demás se atenúan.
- **Interrupciones:** donde la fuerza no se presentó la línea se corta; no se unen puntos separados por una elección sin datos.
- **Eje horizontal:** un lugar por año. En «Todas» las instancias de un mismo año (PASO, general, balotaje) quedan agrupadas, de modo que la distancia entre ellas no se confunda con la que separa dos años.
- **Eje vertical:** se ajusta al rango de la fuerza elegida y no parte de cero, para que las líneas se distingan; el tablero lo aclara en la nota del gráfico.
- La tabla de comprobación ya no incluye la correlación de Spearman. `datos/procesados/tamano_lugar_correlaciones.csv` se sigue generando.

## Límites a tener presentes

- Localidades a menos del 1 % de un límite de categoría: Frontera (9.967), Monte Vera (9.953), Nelson (4.966) y Colonia Aldao
  (2.015). Con la población oficial completa podrían cambiar de categoría.
- Los circuitos subdivididos entre 2023 y 2025 tienen polígonos reconstruidos (unión de hijos). El departamento siempre es el
  correcto, pero dentro de un departamento un circuito podría quedar en una localidad vecina; el nomenclador a mano corrige las
  30 localidades que lo cubren.
- Un circuito cuenta para una sola localidad aunque abarque más de una (menos del 2 % de los circuitos).
