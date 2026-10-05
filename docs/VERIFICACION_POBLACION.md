# Verificación de la población del Censo 2022

Población usada en `docs/TAMANO_DEL_LUGAR.md`: Censo 2022 (INDEC), base por radio censal (datos.gob.ar, dataset 48), sumada por
gobierno local. Proceso: `scripts/asignar_circuitos_a_localidad.py`. Chequeo: `scripts/verificar_poblacion_censo.py`
(escribe `datos/procesados/verificacion_poblacion.csv`).

No se cuenta con la tabla oficial por localidad. El chequeo contrasta la población con tres referencias independientes.

## 1. Contra cifras oficiales conocidas

Cifras definitivas del INDEC difundidas en prensa (no se pudo abrir la tabla del INDEC; conviene confirmarlas allí).

| Territorio | Base propia | Oficial | Diferencia |
|---|---:|---:|---:|
| Provincia de Santa Fe | 3.519.059 | 3.544.908 | −0,73 % |
| Rosario | 1.030.069 | 1.029.619 | +0,04 % |
| Santa Fe | 405.264 | 403.878 | +0,34 % |
| Rafaela | 101.699 | 101.733 | −0,03 % |
| Reconquista | 87.986 | 87.965 | +0,02 % |
| Venado Tuerto | 82.839 | 82.757 | +0,10 % |

El total provincial queda 0,73 % por debajo porque la base por radio cuenta personas en viviendas particulares; en las ciudades
la diferencia es de décimas de punto. Fuentes: [IPEC / Aire de Santa Fe, total provincial](https://www.airedesantafe.com.ar/sociedad/datos-definitivos-del-censo-la-argentina-tiene-4589225-habitantes-y-3544908-viven-santa-fe-n540119);
[Rafaela](https://santafenoticias.com.ar/locales/mas-poco-somos-confirman-que-rafaela-supero-los-100-mil-habitantes-y-podria-sumar-un-concejal.htm);
[Santa Fe](https://www.lt10.com.ar/noticia/440066--censo-2022-la-ciudad-de-santa-fe-tiene-403878-habitantes).

## 2. Contra el padrón electoral (relaciona el censo con los resultados electorales)

Electores 2023 de cada localidad (suma de sus circuitos, según la asignación circuito-localidad) frente a la población de 16 años
o más del mismo censo. Un cociente cercano a 1 confirma a la vez la población y la asignación.

| Indicador | Valor |
|---|---|
| Localidades con electores | 364 |
| Mediana electores / población de 16+ | 1,07 |
| Percentiles 5 y 95 | 0,83 y 1,42 |
| Provincia | 2.827.534 electores / 2.718.068 habitantes de 16+ = 1,04 |
| Localidades fuera de 0,6 a 1,25 | 48, que reúnen el 2,0 % de los electores |

El cociente algo superior a 1 es esperable: el padrón incluye personas empadronadas que no residen en la localidad y registros no
depurados.

**Hallazgo corregido.** El circuito 04250 de 2023 (40.548 electores) había quedado en Ricardone, con un cociente de 9,4, mientras
San Lorenzo quedaba con 0,10. El polígono reconstruido de ese circuito, subdividido entre 2023 y 2025, era parcial. Con la
corrección por padrón (`origen = padron` en `circuito_localidad.csv`) el circuito pasa a San Lorenzo y ambas localidades quedan en
rango. Efecto: en 2023, ciudad pequeña pasa de 10,7 % a 9,2 % de los votos positivos y ciudad grande de 53,1 % a 54,6 %.

**Pendiente.** Josefina conserva un cociente bajo (0,34 en 2019 y 2023): sus 733 electores parecen no cubrir toda la localidad
censal. No se corrigió porque no hay evidencia sobre qué circuito falta.

## 3. Contra las 30 localidades con resultados propios

Votos reconstruidos desde circuitos frente a la fuente por localidad (330 pares localidad-elección): diferencia media absoluta de
0,6 %. Cuatro pares superan el 10 %: Frontera 2019 (dos instancias), San Carlos Sud 2011 general y Santa Clara de Saguier 2015
general, por diferencias entre las propias fuentes.

## Límites

- Cuatro localidades están a menos del 1 % de un límite de categoría: Frontera (9.967), Monte Vera (9.953), Nelson (4.966) y
  Colonia Aldao (2.015).
- Ricardone queda sin circuitos propios en 2023.
- Si el equipo consigue la tabla oficial por localidad, basta reemplazar `poblacion_2022` en
  `datos/referencia/poblacion_gobiernos_locales_censo2022.csv` y volver a correr `scripts/construir_tamano_lugar.py`.
