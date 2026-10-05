# Archivos de salida

Un `.xlsx` por elección, generado por `scripts/generar_xlsx_por_eleccion.py`
según [`docs/CRITERIO_BASE_DE_DATOS.md`](../docs/CRITERIO_BASE_DE_DATOS.md).

**No editar a mano.** Se regeneran corriendo:

```bash
python3 scripts/generar_xlsx_por_eleccion.py
```

## Cobertura

| Elección | Nivel | Unidades | Agrupaciones |
|---|---|---:|---:|
| 2003 General | provincia | 1 | 18 |
| 2007 General | localidad | 30 | 14 |
| 2011 PASO | localidad | 30 | 10 |
| 2011 General | localidad | 30 | 7 |
| 2015 PASO | localidad | 30 | 11 |
| 2015 General | localidad | 30 | 6 |
| 2015 Balotaje | localidad | 30 | 2 |
| 2019 PASO | localidad | 30 | 10 |
| 2019 General | localidad | 30 | 6 |
| 2023 PASO | **circuito** | **523** | 15 |
| 2023 General | localidad | 30 | 5 |
| 2023 Balotaje | localidad | 30 | 2 |

Cada archivo se construye al nivel más fino disponible para esa elección y lo
declara en su hoja `Metadatos`. Las de nivel localidad cubren las 30
localidades de la zona núcleo (Castellanos, Las Colonias y San Martín); la de
2023 PASO cubre los 523 circuitos de los 19 departamentos.

## Hojas

| Hoja | Una fila por | Para qué |
|---|---|---|
| `Resumen` | la elección | lectura rápida |
| `Resultados_ancho` | unidad geográfica | unir con cartografía y mapear |
| `Resultados_largo` | unidad × agrupación | `pandas`, análisis |
| `Nomenclador` | unidad geográfica | cruzar con la capa de circuitos |
| `Metadatos` | clave-valor | procedencia y advertencias |

## Leerlos desde Python

```python
import pandas as pd

df = pd.read_excel("salida/xlsx/2023_PASO_santa_fe_presidente.xlsx",
                   sheet_name="Resultados_largo",
                   dtype={"circuito_id": str, "distrito_id": str})

votos = df[df.tipo_registro == "agrupacion"]          # filtrar SIEMPRE
print(votos.groupby("agrupacion").votos.sum().sort_values(ascending=False))
```

`dtype={"circuito_id": str}` es obligatorio: sin eso pandas convierte `00115`
en `115` y el cruce con la cartografía falla.

## Advertencias

- **2023 es recuento provisorio**, no escrutinio definitivo. Ver
  [`docs/NOTA_METODOLOGICA_2023.md`](../docs/NOTA_METODOLOGICA_2023.md).
- **Los códigos de circuito no son estables entre años**: Santa Fe los
  renumeró en 2023. Nunca cruzar un año con el nomenclador de otro.
- **Las agrupaciones no están homologadas entre años.** En 2003 y 2011 las
  etiquetas incluyen fórmulas con nombre de candidato; desde 2011 son
  alianzas. Para la serie temporal hace falta una tabla de homologación, que
  todavía no existe.
