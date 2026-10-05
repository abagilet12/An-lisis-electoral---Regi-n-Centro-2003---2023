# Swing voters: cambio de ganador por circuito

Pestaña «Swing voters» del tablero.

## Definición y alcance

- **Definición operativa:** los *swing voters* son quienes cambian su comportamiento electoral de una elección a la siguiente.
  Con datos agregados por circuito no se observa a los votantes: se identifican los **lugares** donde el cambio se expresó, es
  decir, los circuitos cuyo ganador (la familia política más votada) es distinto del que ganó en la elección anterior.
- **Aclaración conceptual (Mayer, cap. 1, «What Exactly Is a Swing Voter? Definition and Measurement»):** el autor define al
  *swing voter* como el votante ambivalente que podría votar en cualquier dirección (p. 2) y lo distingue del *party switcher* o
  *floating voter*, quien cruza líneas partidarias de una elección a la siguiente: «son cosas distintas» (pp. 12-13). La
  definición de la pestaña se parece más a la segunda y se aplica a territorios. Un cambio de ganador es compatible con voto
  cruzado, abstención, cambios de oferta o de padrón; los datos agregados no permiten separarlos (inferencia ecológica).
- **Elecciones consideradas:** solo las definitivas, las que definieron presidente: generales 2003, 2007, 2011 y 2019; balotajes
  2015 y 2023. Comparaciones: 2003-2007, 2007-2011, 2011-2015, 2015-2019 y 2019-2023.
- **Sobre el análisis de Schteingart sobre Brasil:** no se pudo abrir el texto (el dominio está bloqueado desde este entorno).
  Se tomó del resumen de búsqueda la lógica de contar las unidades que cambian de ganador y de leer el cambio según el
  tamaño del lugar; ambas ideas se aplican acá (tabla por categoría de localidad).

## Reglas (decididas por el equipo)

1. **Cambio:** el ganador del circuito en la elección b es distinto del que ganó ese circuito en la elección a. **Continuidad:**
   gana la misma fuerza (signo «=» en negro).
2. **Dirección de la flecha:** según el movimiento en la escala izquierda-derecha. Flecha a la derecha si la nueva fuerza queda
   más a la derecha que la que ganó antes en ese circuito; a la izquierda en caso contrario.
3. **Escala:** cinco posiciones (izquierda, centroizquierda, centro, centroderecha, derecha radical) con un **orden fijo dentro
   de cada posición**, de modo que un cambio entre fuerzas de la misma posición también tenga sentido. Está en
   `datos/referencia/ubicacion_familias.csv`, con el respaldo de cada ubicación en las fuentes ya citadas (Murillo y Oliveros
   2024; Murillo, Rubio y Mangonnet 2016; Scaramella 2025; Malamud 2004). Cuando las fuentes no dan una etiqueta, la posición
   es una decisión de investigación y así consta en el CSV. **El orden dentro de cada posición no tiene respaldo en las
   fuentes y es una decisión de investigación.**
4. **Colores y etiquetas:** los de siempre (`docs/CRITERIOS_COLOR.md`); la flecha lleva el color de la fuerza que gana ahora.
5. **Tamaño de las marcas:** se calcula con la cantidad de circuitos y la superficie del mapa (`swTam`), entre 2 y 11 unidades
   de dibujo, para que sea legible donde los circuitos son más chicos.

## Datos y proceso

```
serie_homologada.csv (circuito, familia) ─┐
enlace_circuitos.csv (enlace histórico) ──┼─► scripts/construir_swing.py ─► swing_circuitos.csv, swing_resumen.csv,
cartografía de circuitos (centroides) ────┤                                  salida/datos_swing.json
ubicacion_familias.csv (escala) ──────────┘                                  └─► scripts/agregar_swing.py ─► HTML
```

- **Unidades:** los circuitos de la elección b con polígono en la cartografía (los mismos que usa el resto del tablero).
- **Enlace:** `datos/referencia/enlace_circuitos.csv` (extraído del enlace histórico que el tablero ya usaba) asocia cada circuito
  con el que cubría el mismo territorio en cada elección anterior. Los circuitos sin equivalente (16 a 20 por comparación) se
  dibujan como puntos grises y no se cuentan como cambio.
- **Ganador:** familia más votada del circuito. Un empate exacto lo gana la primera en orden alfabético (con La Libertad Avanza al
  final), igual que el mapa del tablero.
- **Tamaño del lugar:** cada circuito se asigna a una localidad y a una categoría (`docs/TAMANO_DEL_LUGAR.md`).

## Resultados (circuitos comparables)

| Comparación | Circuitos | Continuidad | A la derecha | A la izquierda | % que cambió | Cambio más frecuente |
|---|---:|---:|---:|---:|---:|---|
| 2003-2007 | 499 | 183 | 26 | 290 | 63,3 | Peronismo Federal → Kirchnerismo (192) |
| 2007-2011 | 501 | 182 | 31 | 288 | 63,7 | Centro progresista → Socialismo (101) |
| 2011-2015 | 503 | 114 | 389 | 0 | 77,3 | Socialismo → Cambiemos (208) |
| 2015-2019 | 504 | 438 | 2 | 64 | 13,1 | Cambiemos → Kirchnerismo (64) |
| 2019-2023 | 522 | 51 | 470 | 1 | 90,2 | Cambiemos → La Libertad Avanza (333) |

## Límites

- Tres comparaciones cruzan una general con un balotaje (2011-2015, 2015-2019 y 2019-2023): al haber solo dos fuerzas en el
  balotaje, el cambio de ganador incluye el efecto de la oferta.
- La dirección depende de la escala; con otra ubicación de, por ejemplo, el Peronismo Federal o el Socialismo, cambian los
  conteos de los dos primeros pares.
- Un circuito subdividido entre 2023 y 2025 se compara con el circuito «padre» de la elección anterior.
- La dirección mide el sentido ideológico del cambio de ganador, no su magnitud: no distingue una victoria por un voto de una
  por veinte puntos.
