# Cartografía de circuitos electorales

## Origen y atribución

Estos archivos provienen del repositorio **circuitos_electorales_AR**, de
**Franco Galeano** ([ORCID 0000-0003-3225-7049](https://orcid.org/0000-0003-3225-7049)).

- Repositorio: https://github.com/tartagalensis/circuitos_electorales_AR
- Licencia: **Creative Commons Attribution 4.0 International (CC BY 4.0)**,
  copia completa en `LICENSE`.
- Cita formal: ver `CITATION.cff`.

La licencia permite usar y redistribuir el material, incluso modificado, con la
condición de dar crédito. **Cualquier mapa que publiquemos a partir de estos
datos tiene que citar la fuente.**

## Qué se incorporó

Solo las capas de Santa Fe, de los dos cortes temporales que publica el
repositorio. Las otras 23 provincias no se copiaron porque el proyecto trabaja
sobre Santa Fe; incorporarlas es cuestión de copiarlas del mismo origen.

| archivo | polígonos | numeración | sirve para |
|---|---|---|---|
| `santafe_circuitos_2021.geojson` | 525 | anterior a la renumeración | 2003–2019 |
| `santafe_circuitos_2025.geojson` | 559 | posterior a la renumeración | 2023 |

Propiedades de cada polígono: `circuito`, `codprov` (21 = Santa Fe) y
`coddepto` (001–019). Coordenadas en EPSG:4326. Extensión verificada:
longitud −62,88 a −58,89 y latitud −34,39 a −28,00, que es Santa Fe.

## Verificación de cruce con nuestros datos

Hecha antes de incorporarlos, y es la razón por la que sirven:

- **Corte 2021 contra el nomenclador viejo**: 30 de 30 circuitos encontrados.
- **Corte 2025 contra los 523 circuitos de 2023** (de `establecimientos.csv`):
  503 encontrados, el **96,2%**.
- **Departamento**: coincide en 503 de 503. El `coddepto` del GeoJSON es el
  mismo identificador que el `seccionId` de la DINE, sin necesidad de traducción.

Los códigos del GeoJSON vienen con cinco caracteres (`00055`), uno más que en
los archivos de resultados (`0055`): se completa con un cero a la izquierda.

## Limitaciones registradas

1. **20 circuitos de 2023 sin polígono en el corte 2025**, entre ellos `00550`
   (Esperanza). Son circuitos que cambiaron entre 2023 y 2025, que es la
   distancia temporal entre nuestro dato y la cartografía disponible. Hay que
   resolverlos a mano o tomando su polígono del corte 2021.
2. **9 polígonos vacíos en el corte 2021**, todos sub-circuitos con letra
   (`0365A`, `0368B`, `0368C`, `0368D`, `0230A`, `0285B`…). El archivo los
   declara pero sin geometría. Vuelven a ser los sub-circuitos, que ya venían
   dando problemas con la renumeración.
3. **El GeoJSON no trae nombre de localidad**, solo circuito y departamento. No
   resuelve por sí solo el mapeo circuito → localidad; lo que aporta es la
   geometría para hacerlo por cruce espacial, o para dibujar el mapa una vez que
   el mapeo exista por otra vía.
4. El repositorio advierte que incluye **circuitos reconstruidos manualmente**
   para provincias sin cartografía oficial. Habría que averiguar si Santa Fe es
   una de ellas antes de tratar los límites como oficiales.
