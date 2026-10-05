# Estructura del tablero y criterio de reagrupación

El tablero (`salida/voto_santafesino.html`) se ordena por la pregunta que responde cada
pestaña, no por el tipo de gráfico. Marco conceptual de la investigación: nacionalización,
sistema de partidos, coordinación multinivel, sistema electoral nacional y realineamiento
vertical. Esos conceptos orientan qué se agrupa y en qué orden; el tablero no los define.

| Pestaña | Pregunta | Secciones |
|---|---|---|
| Objetivos, método y base de datos | Qué se hizo y con qué datos | Objetivos · Recolección y procesamiento de los datos · Advertencias y fuentes |
| Evolución del voto | Cómo cambia el voto en el territorio | Evolución del voto a Presidente en Santa Fe 2003-2023 por circuito electoral (mapa de la serie, con tres líneas de interpretación) · El voto departamento por departamento · Comparación de las elecciones definitivas 2003 - 2023 en Santa Fe |
| Distribución del electorado | Cómo se distribuye el voto (lectura de detalle) | Resultados comparados, 2003-2023 · El voto circuito por circuito |
| Análisis estadístico | Qué dicen las tablas y los indicadores | Tabla por elección · Composición por departamento · Volatilidad y desafección |
| Hallazgos | Qué indicadores sintetizan la serie | Resumen de 5 números · Evolución de las fuerzas políticas (las tres que ganaron la presidencia) · El voto según el tamaño del lugar (`docs/TAMANO_DEL_LUGAR.md`) |
| Elecciones | Ficha de cada elección, por etiqueta oficial | (generada por `scripts/agregar_pestanas.py`) |
| Partidos | Ficha de cada partido | (generada por `scripts/agregar_pestanas.py`) |

## Criterios

- Las lecturas cartográficas de conjunto van en «Evolución del voto»; las tablas y lecturas de
  detalle, en «Distribución del electorado».
- Las líneas de interpretación se redactan solo con cifras que se pueden verificar en la base
  (porcentaje sobre votos positivos, recuento provisorio, familias políticas) y se formulan como
  lectura, no como causa.
- Títulos, paleta (`#010318` → `#07169C` para la interfaz), colores de familias
  (`docs/CRITERIOS_COLOR.md`), etiquetas (`docs/CRITERIO_DERECHA_LIBERTARIA.md`) y redacción
  académica se mantienen en todas las pestañas.

## Pendiente de decisión

- El análisis por tamaño del lugar usa las 30 localidades con resultados propios y deja vacías las categorías
  rural y ciudad grande (`docs/TAMANO_DEL_LUGAR.md`).
- Hay dos mapas por circuito: el de la serie (pestaña «Evolución del voto», con ficha histórica) y
  «El voto circuito por circuito» (pestaña «Distribución del electorado»).
- «Resultados comparados» (la serie en cifras) quedó en «Distribución del electorado».
