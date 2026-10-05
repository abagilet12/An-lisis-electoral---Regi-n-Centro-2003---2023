# Criterios de color para partidos, alianzas y candidatos

El color identifica una **familia política** (el campo `familia` de
`datos/referencia/homologacion_agrupaciones.csv`). Los valores vigentes están en
`datos/referencia/colores_familias.csv`; el tablero los toma de allí.

## Paleta vigente

| Familia | Color | Hex |
|---|---|---|
| Kirchnerismo | azul claro | `#4fa8ea` |
| Peronismo Federal | azul oscuro | `#12338a` |
| Socialismo | rojo | `#d7263d` |
| La Libertad Avanza (desde 2023) | violeta | `#7b3fc4` |
| Derecha libertaria (anterior a 2023) | violeta claro | `#b79ae6` |
| Cambiemos / Juntos por el Cambio | amarillo | `#f2c200` |
| Centro progresista no peronista | naranja | `#e8782a` |
| Centroderecha liberal | rosa | `#e87ba4` |
| Izquierda | verde | `#008300` |
| Centroizquierda no peronista | verde azulado | `#0f8b8d` |
| Unión Cívica Radical | bordó | `#8c2f39` |
| Derecha nacionalista | marrón | `#6b4f2a` |
| Otros / Otras fuerzas | gris | `#9a9a92` |

Nombres: «Peronismo kirchnerista» pasa a **Kirchnerismo**, «Peronismo no kirchnerista»
a **Peronismo Federal** y «Socialismo y progresismo santafesino» a **Socialismo**. La derecha libertaria se divide
en dos familias por período (`docs/CRITERIO_DERECHA_LIBERTARIA.md`).
El eje `bloque` (Kirchnerismo / Peronismo no kirchnerista / No kirchnerismo) no cambia.

## Reglas

1. **Un color por familia, y una familia por color.** Ningún par de familias comparte
   color. Si una asignación nueva coincide con la de otra familia, se cambia la de la
   familia que no fue indicada expresamente. Así, el violeta que tenía el centro
   progresista pasó a La Libertad Avanza y el centro progresista pasó a naranja.
2. **El color no depende del puesto ni de la elección.** Una familia tiene el mismo
   color en todas las instancias, mapas, gráficos y fichas.
3. **Las alianzas toman el color de su familia.** Cada etiqueta (partido, alianza,
   frente, coalición o fórmula) hereda el color de la familia que le asigna la
   homologación. No se mezclan colores: una alianza no tiene color propio.
   Ejemplos: Frente para la Victoria, Frente de Todos y Unión por la Patria →
   Kirchnerismo; Cambiemos y Juntos por el Cambio → amarillo.
4. **Alianzas entre familias.** Cuando una alianza reúne fuerzas de familias
   distintas, se colorea con la familia de quien encabeza la fórmula presidencial,
   que es la que consigna la homologación. Cambiar esa decisión es editar la
   columna `familia` del CSV, no el código.
5. **Candidatos.** Una candidatura se representa con el color de la etiqueta con la
   que se presentó, es decir, con el de la familia de esa etiqueta, aunque el
   candidato cambie de espacio en otra elección.
6. **Etiquetas sin familia asignada** y las fuerzas no individualizadas se dibujan en
   gris («Otros» / «Otras fuerzas»). Una etiqueta que hoy no figura en la
   homologación queda en gris hasta que se la clasifique.
7. **Intensidad.** Los mapas de intensidad usan una escala del blanco al color pleno
   de la familia; el color de una familia nunca se usa para otra cosa.
8. **Colores reservados para la interfaz.** El tablero usa solo la escala
   `#010318` → `#07169C` para títulos, controles y énfasis. Los indicadores que no
   son partidos (participación, voto en blanco y voto nulo) usan tonos de esa escala y grises azulados
   y no los colores de la tabla.
