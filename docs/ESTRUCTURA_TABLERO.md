# Estructura del tablero y criterio de reagrupación

El tablero (`salida/voto_santafesino.html`) se ordena por la pregunta que responde cada
pestaña, no por el tipo de gráfico. Marco conceptual de la investigación: nacionalización,
sistema de partidos, coordinación multinivel, sistema electoral nacional y realineamiento
vertical. Esos conceptos orientan qué se agrupa y en qué orden; el tablero no los define.

| Pestaña | Pregunta | Secciones |
|---|---|---|
| Objetivos, método y base de datos | Qué se hizo y con qué datos | Objetivos · Recolección y procesamiento de los datos · Advertencias y fuentes |
| Evolución del voto | Cómo cambia el voto en el territorio | Evolución del voto a Presidente en Santa Fe 2003-2023 por circuito electoral (mapa de la serie, con tres líneas de interpretación) · El voto departamento por departamento · Comparación de las elecciones definitivas 2003 - 2023 en Santa Fe |
| Swing voters | Dónde cambió el ganador entre elecciones definitivas | Swing voters (mapa con flechas y vista ampliada) · Las cinco comparaciones · El cambio según el tamaño del lugar (`docs/SWING_VOTERS.md`) |
| Análisis estadístico | Qué dicen las tablas y los indicadores | Resultados comparados, 2003-2023 · Tabla por elección · Composición por departamento · Volatilidad y desafección |
| Hallazgos | Qué indicadores sintetizan la serie | Resumen de 5 números · Evolución de las fuerzas políticas (las tres que ganaron la presidencia) · El voto según el tamaño del lugar (`docs/TAMANO_DEL_LUGAR.md`) |
| Elecciones | Ficha de cada elección, por etiqueta oficial | (generada por `scripts/agregar_pestanas.py`) |
| Partidos | Ficha de cada partido | (generada por `scripts/agregar_pestanas.py`) |

## Criterios

- Las lecturas cartográficas van en «Evolución del voto» (un solo mapa por circuito, el de la serie, con ficha
  histórica); las tablas y los indicadores, en «Análisis estadístico». La pestaña «Distribución del electorado»
  se disolvió al quedar con una sola sección.
- Las líneas de interpretación se redactan solo con cifras que se pueden verificar en la base
  (porcentaje sobre votos positivos, recuento provisorio, familias políticas) y se formulan como
  lectura, no como causa.
- Títulos, paleta (`#010318` → `#07169C` para la interfaz), colores de familias
  (`docs/CRITERIOS_COLOR.md`), etiquetas (`docs/CRITERIO_DERECHA_LIBERTARIA.md`) y redacción
  académica se mantienen en todas las pestañas.
