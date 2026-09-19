# Cartografía de circuitos electorales de Santa Fe

## Origen y licencia

Las dos capas base son de **Franco Galeano**, bajo licencia **CC BY**. Ver
`FUENTE.md`, `LICENSE` y `CITATION.cff`. **Cualquier mapa publicado debe
citarlo.**

| Capa | Polígonos | Sin geometría |
|---|---:|---:|
| `santafe_circuitos_2021.geojson` | 525 | 9 |
| `santafe_circuitos_2025.geojson` | 559 | 0 |

EPSG:4326. Propiedades: `circuito`, `codprov`, `coddepto`.

## Por qué hay capas reconstruidas

Ningún corte coincide con los circuitos de todas las elecciones, por dos
motivos distintos que conviene no confundir:

**1. Relleno de ceros (cosmético).** Los datos de 2003-2015 usan códigos de
cuatro dígitos (`0001`) y la cartografía cinco (`00001`). Parecía una
renumeración y no lo es: normalizando cruzan casi todos.

**2. Subdivisión de circuitos (real).** Entre 2023 y 2025 la provincia
**partió** circuitos: 20 códigos de 2023 no existen como tales en el corte
2025, y entre ellos está buena parte de Rosario —el 22,8 % de los votos—.
No están tampoco en el corte 2021, así que no se recuperan de ahí.

La subdivisión sigue una regla regular: el circuito `0XYZ0` se partió en
`0XYZ1`…`0XYZ9`. `scripts/construir_capa_circuitos.py` reconstruye el
polígono **uniendo los hijos**, sin trabajo manual y sin perder superficie.

## Capas listas para usar

Una por año, indexada por el código **de los datos** para que el cruce sea
directo:

```
santafe_circuitos_<anio>_reconstruido.geojson
```

Cada polígono lleva `origen`: `directo` o `union de N`.

## Cobertura alcanzada

| Elección | Circuitos | Con polígono | % votos |
|---|---:|---:|---:|
| 2003 General | 516 | 510 | 99,83 % |
| 2007 General | 521 | 515 | 99,83 % |
| 2011 PASO / Gral | 522 | 517 | 99,99 % |
| 2015 PASO / Gral / Bal | 523 | 519 | 99,99 % |
| 2019 PASO / Gral | 527 | 524 | 100,00 % |
| 2023 PASO / Gral / Bal | 523 | 522 | 99,99 % |

Los circuitos sin polígono son sub-circuitos con letra (`0230A`, `0365A`),
que vienen vacíos en la cartografía de origen. Pesan menos del 0,2 % de los
votos.

## Advertencias para el mapa

- **Dos cortes, no uno.** 2003-2019 usan el corte 2021 y 2023 el 2025. Las
  capas reconstruidas ya resuelven el cruce dentro de cada año, pero **no se
  pueden superponer geometrías entre años** sin traducir códigos.
- **Rosario y Santa Fe capital** concentran muchísimos circuitos en poca
  superficie. Un mapa provincial plano los muestra como manchas ilegibles:
  necesitan recuadros ampliados.
- **Departamentos**: se obtienen disolviendo por `coddepto`, sin capa aparte.
- **Localidades**: no se pueden mapear todavía; requieren el nomenclador
  circuito→localidad, hoy relevado en 30 de 523 circuitos.
