# Criterio: derecha libertaria y La Libertad Avanza

## Regla

- **Antes de 2023** la familia política se llama **Derecha libertaria**. En Santa Fe
  solo la ocupa Unite por la Libertad y la Dignidad (2019, PASO y general). Ninguna otra
  etiqueta anterior a 2023 está clasificada ahí.
- **Desde 2023** todo voto de la derecha libertaria, incluido el de La Libertad Avanza,
  se computa en la familia **La Libertad Avanza**. Cubre PASO, general y balotaje de 2023
  y cualquier elección posterior.
- Los años anteriores a 2023 no se modifican.

Fundamento: La Libertad Avanza emerge como fuerza principal de las derechas con una
verticalidad y una rapidez que no permiten tratarla como continuación de las candidaturas
libertarias previas. La continuidad con Unite queda abierta como pregunta de
investigación y no como supuesto del dato.

## Dónde vive el criterio

| Capa | Archivo | Qué hace |
|---|---|---|
| Decisión | `datos/referencia/homologacion_agrupaciones.csv` | columna `familia`: `Derecha libertaria` hasta 2019, `La Libertad Avanza` en 2023 |
| Guarda | `scripts/homologar.py` | se detiene si la tabla viola la regla |
| Serie | `datos/procesados/serie_homologada.csv` | se regenera con `scripts/homologar.py` |
| Tablero | `salida/datos_analisis.json` | se regenera con `scripts/preparar_datos_analisis.py` |
| Fichas | `salida/datos_fichas.json` | `scripts/asignar_familia_fichas.py` asigna la familia a cada etiqueta |
| Excel | `salida/xlsx/2023_*` | columna `familia` y hoja `Resumen` |
| Presentación | `salida/voto_santafesino.html` | mapas, tablas, series y fichas; la etiqueta, el color y el índice de familia |

## Control

`python3 scripts/verificar_derecha_libertaria.py` comprueba que (1) la regla se cumple fila
por fila, (2) los votos de las dos familias suman lo mismo que las etiquetas originales
del linaje (Unite en 2019; La Libertad Avanza en 2023), (3) el dato por departamento coincide
con el dato por circuito, y (4) ninguna otra etiqueta anterior a 2023 tiene rasgos
libertarios sin estar clasificada. Además escribe
`datos/procesados/derecha_libertaria_pre2023.csv`, con cada voto de la derecha libertaria
anterior a 2023 por elección, etiqueta y departamento.

## Votos aislados (circuitos, recuento provisorio)

| Elección | Familia | Votos |
|---|---|---:|
| 2019 PASO | Derecha libertaria (Unite) | 58.687 |
| 2019 general | Derecha libertaria (Unite) | 40.315 |
| 2023 PASO | La Libertad Avanza | 646.315 |
| 2023 general | La Libertad Avanza | 657.813 |
| 2023 balotaje | La Libertad Avanza | 1.278.243 |

## Consecuencias para la lectura

- Las series por familia muestran dos fuerzas distintas, con un solo punto cada una
  (2019 y 2023). No es un corte de dato: es el criterio.
- La volatilidad de Pedersen 2019-2023 suma el valor de Unite y el de La Libertad Avanza,
  porque son fuerzas distintas; sería menor si se las considerara una sola.
