# Homologación: cómo se vuelven comparables los años

Hacer comparable una serie electoral de veinte años exige resolver **tres
problemas distintos**. Conviene no confundirlos, porque solo el primero es
técnico.

## Problema 1 — La escritura varía (mecánico)

La misma fuerza aparece escrita distinto según la fuente: `ALIANZA FRENTE
PARA LA VICTORIA` y `Alianza Frente para la Victoria`; `ALIANZA CAMBIEMOS` y
`CAMBIEMOS`; `MOVIMIENTO DE ACCION VECINAL` y `MOVIMIENTO DE ACCIÓN VECINAL`.
Son 82 etiquetas distintas para 52 fuerzas.

Lo resuelve la columna `agrupacion_homologada`. No hay decisión que tomar
acá: es unificar ortografía.

## Problema 2 — La continuidad política (interpretativo)

Decidir que el Frente para la Victoria (2003-2015), el Frente de Todos (2019)
y Unión por la Patria (2023) son **la misma corriente** es una decisión de
investigación, no un hecho del dato. Lo mismo vale para Cambiemos → Juntos
por el Cambio, o para considerar a La Libertad Avanza heredera de Unite.

Esto se explicita en dos columnas, deliberadamente separadas:

- **`familia`**: linaje partidario. Doce categorías, de `Peronismo
  kirchnerista` a `Derecha libertaria`.
- **`bloque`**: el eje kirchnerismo / no kirchnerismo que el plan de
  investigación toma como estructurante desde el conflicto agrario de 2008.
  Deja al peronismo no kirchnerista como categoría propia, porque colapsarlo
  en cualquiera de los dos polos decidiría por adelantado lo que se quiere
  analizar.

**El criterio vive en `datos/referencia/homologacion_agrupaciones.csv`, no en
el código.** Para cambiarlo se edita el CSV y se vuelve a correr
`scripts/homologar.py`. Ningún script fija una interpretación.

### Decisiones que conviene revisar

La clasificación actual es un punto de partida razonable, no una verdad. Las
cinco que más pesan:

1. **FPV → Frente de Todos → UxP como una sola corriente.** Es lo habitual en
   la literatura, pero el Frente de Todos incorpora en 2019 a Massa, que en
   2015 encabezaba UNA, clasificado acá como peronismo no kirchnerista. La
   continuidad es de etiqueta y de coalición, no de elenco.
2. **2007 se clasifica por fórmula, no por agrupación**, porque la fuente de
   ese año identifica candidatos y no alianzas. Carrió-Giustiniani se asigna
   a `Centro progresista no peronista`, pero Giustiniani es socialista
   santafesino: en Santa Fe esa fórmula tiene un componente que la
   clasificación nacional no captura.
3. **La Libertad Avanza aparece sin antecedente.** Se la clasificó como
   `Derecha libertaria`, familia que en 2019 solo ocupaba Unite (1,8 %). Si se
   la considera heredera, hay continuidad; si no, es irrupción pura. El dato
   no lo decide.
4. **El socialismo santafesino** es el caso más sensible para esta
   investigación: 42,7 % en 2011 y desaparecido después. Se mantuvo como
   familia propia en vez de fundirlo en un progresismo genérico, porque su
   colapso es un fenómeno a explicar y no un detalle de etiquetado.
5. **La UCR** aparece suelta en 2003 y 2011 (UDESO) y después se disuelve
   dentro de Cambiemos. No se la imputó retroactivamente a Cambiemos: eso
   supondría una continuidad que en 2011 todavía no existía.

## Problema 3 — El universo geográfico (el más grave)

**Homologar los nombres no alcanza.** Una serie solo es comparable si además
las unidades geográficas son las mismas todos los años.

Este proyecto tiene dos recortes que **no se pueden mezclar**:

| Universo | Qué cubre | Instancias |
|---|---|---|
| `zona_nucleo_30_localidades` | Castellanos, Las Colonias y San Martín | 11 (2007-2023) |
| `provincia_completa` | los 19 departamentos | 7 (2003 y 2023) |

Comparar el 16,1 % del kirchnerismo en 2003 —provincia entera, 1.685.735
votos— con el 34,4 % de 2007 —30 localidades, 110.542 votos— no mide un
cambio político: mide un cambio de recorte.

Por eso `serie_homologada.csv` lleva la columna `universo`, y **toda serie
temporal debe filtrarla antes de agregar**:

```python
import pandas as pd
s = pd.read_csv("datos/procesados/serie_homologada.csv")
nucleo = s[s.universo == "zona_nucleo_30_localidades"]     # SIEMPRE filtrar
```

Una elección que existe en dos niveles a la vez (la PASO 2023 está por
circuito y por localidad) aparece **dos veces**, una por universo. Sumar sin
filtrar la cuenta doble.

## La serie válida

Zona núcleo, elecciones generales, porcentaje sobre votos positivos:

| Familia | 2007 | 2011 | 2015 | 2019 | 2023 |
|---|---:|---:|---:|---:|---:|
| Cambiemos | — | — | 45,1 | 57,2 | 28,1 |
| Socialismo y progresismo santafesino | — | 42,7 | 3,7 | — | — |
| Derecha libertaria | — | — | — | 1,8 | 39,1 |
| Peronismo no kirchnerista | 36,6 | 11,3 | 25,7 | 7,8 | 13,6 |
| Peronismo kirchnerista | 34,4 | 36,2 | 23,9 | 30,9 | 18,0 |
| Centro progresista no peronista | 24,4 | 1,7 | — | — | — |
| Unión Cívica Radical | — | 6,6 | — | — | — |
| Izquierda | 1,1 | 1,5 | 1,6 | 1,1 | 1,1 |

Eje kirchnerismo / no kirchnerismo:

| Bloque | 2007 | 2011 | 2015 | 2019 | 2023 |
|---|---:|---:|---:|---:|---:|
| Kirchnerismo | 34,4 | 36,2 | 23,9 | 30,9 | 18,0 |
| Peronismo no kirchnerista | 36,6 | 11,3 | 25,7 | 7,8 | 13,6 |
| No kirchnerismo | 29,0 | 52,5 | 50,4 | 61,3 | 68,3 |

Falta 2003 en este universo: solo existe a nivel provincial.

## Advertencia sobre las PASO

Las PASO no son comparables con las generales aunque sean del mismo año: la
oferta es más fragmentada y el voto se reparte entre listas internas. Al
construir series conviene usar **una sola instancia** —generales, por lo
común— y tratar las PASO por separado.
