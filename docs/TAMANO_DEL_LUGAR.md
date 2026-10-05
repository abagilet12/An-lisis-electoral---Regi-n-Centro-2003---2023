# El voto según el tamaño del lugar

## Escala demográfica

Definida en `datos/referencia/escala_tamano_lugar.csv` (se edita ahí, no en el código):

| Categoría | Habitantes |
|---|---|
| Rural | menos de 2.000 (el valor 2.000 se asigna aquí) |
| Pueblo | 2.001 a 5.000 |
| Ciudad pequeña | 5.001 a 10.000 |
| Ciudad intermedia | 10.001 a 50.000 |
| Ciudad grande | 50.001 a 1.000.000 |

## Datos

- **Voto por localidad:** `datos/procesados/serie_homologada.csv`, filas de nivel `localidad`
  (30 localidades de Castellanos, Las Colonias y San Martín; 11 instancias de 2007 a 2023).
  No existen resultados por localidad para 2003.
- **Población:** Censo 2022 (INDEC), base agregada por radio censal (datos.gob.ar, dataset 48).
  `scripts/construir_poblacion_censo2022.py` suma la población de los radios de cada gobierno
  local y escribe `datos/referencia/poblacion_localidades_censo2022.csv`. La suma provincial
  (3.519.059) corresponde a viviendas particulares, por lo que queda levemente por debajo del total
  publicado por INDEC. **Si el equipo tiene la tabla oficial por localidad, basta reemplazar ese CSV.**
- **Proceso:** `scripts/construir_tamano_lugar.py` clasifica, cruza y controla; escribe
  `datos/procesados/tamano_lugar.csv`, `datos/procesados/tamano_lugar_correlaciones.csv` y
  `salida/datos_tamano_lugar.json`. `scripts/agregar_tamano_lugar.py` lo inserta en el HTML.

## Controles realizados

1. Las 30 localidades se asocian a un único gobierno local censal, dentro del departamento correcto.
2. Cada elección contiene las 30 localidades y la suma de votos por familia coincide con
   `serie_localidad.csv`.
3. Relación electores/población dentro de 0,5 a 0,95, salvo **Josefina (0,27)**: su padrón varía entre
   706 y 1.403 electores según el año, lo que sugiere que el nomenclador electoral no cubre toda la
   localidad censal. Conviene revisarla.
4. Localidades cerca de un límite de categoría (±3 %): Colonia Aldao (2.015), Santa Clara de Saguier
   (2.057), María Juana (4.910) y **Frontera (9.967, a 33 habitantes de ciudad intermedia)**. Con la
   población oficial completa, Frontera podría pasar de categoría.

## Resultado de la clasificación

| Categoría | Localidades |
|---|---:|
| Rural | 0 |
| Pueblo | 15 |
| Ciudad pequeña | 10 |
| Ciudad intermedia | 5 |
| Ciudad grande | 0 |

Las 30 localidades reúnen alrededor del 6,4 % de los votos positivos de la provincia. Las categorías
rural y ciudad grande quedan sin datos: para cubrirlas hace falta resultados por localidad fuera de los
tres departamentos de la zona núcleo (en particular Rosario y Santa Fe).
