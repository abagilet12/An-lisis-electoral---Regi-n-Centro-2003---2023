# Validación de la base de datos electorales de Santa Fe (2011-2023)

Archivo recibido: `datos/crudos/otras_fuentes/datos_electorales_presidente_santafe_2011_2023.csv`
(104 filas, provincia de Santa Fe, categoría Presidente). Se guardó sin modificar.

## Qué contiene

- **Diez de las doce instancias:** PASO, generales y balotaje de 2011 a 2023. **Faltan
  2003 y 2007**, que seguimos cubriendo con los Excel de la DINE y nuestra base.
- Una fila por partido o alianza e instancia, más las filas de blanco, nulo e impugnado.
  Hay 35 etiquetas partidarias distintas.
- Todos los porcentajes y votos son de **recuento provisorio**. Coinciden exactamente
  con nuestra base en 29 de 74 filas (todas las de 2023 y las PASO 2011).

## Problemas del archivo que conviene saber

1. **Los porcentajes mezclan dos denominadores.** Los partidos van sobre votos
   positivos y blanco, nulo e impugnado sobre el total de votantes. Por eso la
   suma por instancia da entre 102 y 107 %. Para comparar hay que recalcular desde
   los votos.
2. **Generales 2011: electores y votantes están mal.** Dice 1.603.597 electores y
   1.205.980 votantes, pero los votos suman 1.830.040 y la DINE informa 2.443.309
   electores y 1.854.207 votantes. Los votos de los partidos no tienen ese problema.
3. **Los nombres no son siempre los oficiales:** «Frente Patriota» (2019) y «Frente
   Patriota Federal» (2023) son etiquetas distintas, y «Coalición Cívica-ARI» no
   repite el nombre oficial de la DINE.

## Comparación con la fuente oficial (ganador de cada instancia)

Diferencia porcentual contra el escrutinio definitivo de la DINE:

| Elección | Ganador | DINE definitivo | Base propia | Base nueva (CSV) |
|---|---|---:|---:|---:|
| 2011 Paso | Alianza Frente Para La Victoria | 676.812 | 667.186 (-1.4 %) | 667.186 (-1.4 %) |
| 2011 General | Alianza Frente Para La Victoria | 758.721 | 753.556 (-0.7 %) | 748.999 (-1.3 %) |
| 2015 Paso | Alianza Frente Para La Victoria | 550.970 | 547.865 (-0.6 %) | 547.529 (-0.6 %) |
| 2015 General | Alianza Cambiemos | 712.100 | 710.457 (-0.2 %) | 704.358 (-1.1 %) |
| 2015 Balotaje | Alianza Cambiemos | 1.141.121 | 1.137.708 (-0.3 %) | 1.136.478 (-0.4 %) |
| 2019 General | Juntos Por El Cambio | 937.611 | 934.867 (-0.3 %) | 928.289 (-1.0 %) |

El CSV queda entre 0,4 y 1,4 % por debajo del definitivo y, en cuatro de las seis
instancias comparables, más lejos que nuestra base. Sirve para contrastar y
como segunda fuente provisoria, pero no para reemplazar el definitivo.

## Qué aporta de nuevo

Completa tres partidos menores que nuestra base no tenía en la PASO 2011: Del Campo
Popular (3.775 votos), Movimiento de Acción Vecinal (2.458) y Proyecto Sur (12.496).
En el resto de las instancias el universo de partidos coincide con el de la base.

## ¿Resuelve las preguntas pendientes?

No. Es una base de **resultados**, sin composición de alianzas ni ubicación
ideológica. Lo que cambia es el alcance de lo que hay que ubicar.

| Pregunta pendiente | ¿Cambia con esta base? |
|---|---|
| Composición de las alianzas 2015-2023 | **No.** Sigue haciendo falta el registro de alianzas o las actas de la CNE. |
| Escala de siete posiciones y definición de «radical» | **No.** Es una decisión de método. |
| Frente que hereda la posición de su socio hegemónico | **No.** |
| Campo peronista / no peronista como eje separado | **No.** |
| Fuentes de ubicación para 2003-2023 | **No**, pero ahora se sabe qué ubicar: las 35 etiquetas de 2011-2023 más las de 2003 y 2007. |
| Las «dos consideraciones» sobre etiquetas y alianzas | **No.** Sigue sin respuesta. |
