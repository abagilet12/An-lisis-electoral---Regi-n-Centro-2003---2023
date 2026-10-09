# Swing voters: cambio de ganador por circuito

Pestaña «Swing voters» del tablero.

## Definición y alcance

- **Definición operativa:** los *swing voters* son quienes cambian su comportamiento electoral de una elección a la siguiente.
  Con datos agregados por circuito no se observa a los votantes: se identifican los **lugares** donde el cambio se expresó, es
  decir, los circuitos cuyo ganador (la familia política más votada) es distinto del que ganó en la elección anterior.
- **Aclaración conceptual (Mayer, 2008, cap. 1):** el autor define al *swing voter* como el votante ambivalente que podría votar en
  cualquier dirección (Mayer, 2008: 2) y lo distingue del *party switcher* o *floating voter*, quien cruza líneas partidarias de una
  elección a la siguiente: no son lo mismo (Mayer, 2008: 12-13). La
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
3. **Escala:** criterio de Bobbio (1994), documentado en `docs/CRITERIO_IDEOLOGICO_BOBBIO.md`. Cada familia tiene un puntaje de
   igualitarismo (menor, más igualitaria, más a la izquierda) que define un orden estricto y cinco posiciones (izquierda,
   centroizquierda, centro, centroderecha y derecha radical). Datos: `datos/referencia/ubicacion_familias.csv`. La posición se
   apoya en las fuentes citadas; el puntaje fino dentro de una posición es una codificación de investigación.
4. **Colores y etiquetas:** los de siempre (`docs/CRITERIOS_COLOR.md`); la flecha lleva el color de la fuerza que gana ahora.
5. **Tamaño de las marcas:** se calcula con la cantidad de circuitos y la superficie del mapa (`swTam`), entre 2 y 11 unidades
   de dibujo, para que sea legible donde los circuitos son más chicos.
6. **Diseño de la flecha** (`swFlecha`): flecha de línea, con asta fina y punta abierta en «V», sin relleno ni contorno, trazada con el
   color de la fuerza que gana. Las proporciones siguen la flecha de referencia del equipo; el grosor y la punta tienen un mínimo para que
   la flecha se lea aun cuando es muy chica. Al no tener relleno, las flechas que se superponen se siguen distinguiendo. Solo cambia el
   dibujo: el criterio de color y de sentido es el de las reglas 2 y 4.

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

| Comparación | Circuitos | Continuidad | A la derecha | A la izquierda | % que cambió | Dentro de una misma posición | Cambio más frecuente |
|---|---:|---:|---:|---:|---:|---:|---|
| 2003-2007 | 499 | 183 | 27 | 289 | 63,3 | 12 | Peronismo Federal → Kirchnerismo (192) |
| 2007-2011 | 501 | 182 | 2 | 317 | 63,7 | 169 | Centro progresista → Socialismo (101) |
| 2011-2015 | 503 | 114 | 389 | 0 | 77,3 | 1 | Socialismo → Cambiemos (208) |
| 2015-2019 | 504 | 438 | 2 | 64 | 13,1 | 0 | Cambiemos → Kirchnerismo (64) |
| 2019-2023 | 522 | 51 | 470 | 1 | 90,2 | 0 | Cambiemos → La Libertad Avanza (333) |

## Límites

- Tres comparaciones cruzan una general con un balotaje (2011-2015, 2015-2019 y 2019-2023): al haber solo dos fuerzas en el
  balotaje, el cambio de ganador incluye el efecto de la oferta.
- La dirección depende de la escala: en 2007-2011, 169 de 319 cambios ocurren entre fuerzas de la misma posición y su sentido
  depende del puntaje fino (ver la sensibilidad en `docs/CRITERIO_IDEOLOGICO_BOBBIO.md`).
- Un circuito subdividido entre 2023 y 2025 se compara con el circuito «padre» de la elección anterior.
- La dirección mide el sentido ideológico del cambio de ganador, no su magnitud: no distingue una victoria por un voto de una
  por veinte puntos.
