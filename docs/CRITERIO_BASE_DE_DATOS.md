# Criterio unificado de confección de la base de datos

Este documento fija cómo se construyen las tablas y los archivos de salida.
Vale para todo lo que ya existe y para todo lo que se agregue. Si una fuente
nueva no encaja, se adapta la fuente al criterio, no al revés.

## 1. Alcance

Categoría **Presidente y Vice**, provincia de **Santa Fe** (distrito 21),
**2003-2023**. Son 12 instancias de votación. Todo lo ajeno a Santa Fe vive en
`datos/reservados/` y no entra en esta base.

## 2. Flujo

```
datos/crudos/      originales, jamás editados
      ↓  scripts/parse_*.py  ·  scripts/agregar_*.py
datos/procesados/  CSV tidy, una fila por observación
      ↓  scripts/generar_xlsx_por_eleccion.py
salida/xlsx/       un .xlsx por elección, listo para usar
```

Los crudos no se tocan nunca. Todo lo derivado se regenera corriendo los
scripts: si un número está mal, se arregla el script, no el archivo.

## 3. Niveles de agregación

Cuatro niveles, del más fino al más grueso:

| Nivel | Unidad | Clave |
|---|---|---|
| Mesa | mesa electoral | `mesa_id` |
| **Circuito** | **circuito electoral** | **`circuito_id`** |
| Localidad | localidad | `localidad` |
| Departamento | departamento | `seccion_id`, `seccion` |
| Provincia | distrito | `distrito_id` |

**El circuito es la unidad de referencia**: es la menor unidad con identidad
geográfica estable y es la que se usa para mapear. Departamento y provincia
se obtienen sumando circuitos. La localidad **no** se deriva de los datos:
requiere un nomenclador circuito→localidad relevado a mano.

Cada archivo de salida se construye al **nivel más fino disponible** para esa
elección, y lo declara en su hoja de metadatos.

## 4. Nomenclador

`circuito_id` se almacena **como texto, con los ceros a la izquierda tal como
los trae la fuente**. Nunca como número: `00115` no es `115`.

Para comparar entre fuentes se normaliza quitando los ceros de la izquierda,
porque el relleno varía (la DINE usa 5 dígitos, los `.xlsx` por localidad
usan 4). Esa normalización es solo para el cruce; lo que se guarda es el
código original.

**Los códigos de circuito no son estables entre años.** Santa Fe renumeró sus
circuitos en 2023: `0043` pasó a `0430`. Por eso el nomenclador tiene columna
`anio` y **jamás se cruza un año con el nomenclador de otro**.

## 5. Tipos de registro

La columna `tipo_registro` distingue qué es cada fila. Evita tener que
adivinar por el nombre:

| Valor | Qué es |
|---|---|
| `agrupacion` | votos de una agrupación política |
| `lista` | lista interna dentro de una agrupación (solo PASO) |
| `formula` | fórmula de precandidatos dentro de una agrupación (solo PASO) |
| `blancos`, `nulos`, `impugnados`, `recurridos`, `comando` | votos no positivos |
| `positivo` | suma de las agrupaciones |
| `validos` | positivos + blancos |
| `total` | total de votantes |
| `inscriptos` | padrón |
| `participacion` | porcentaje de votantes |

**Al sumar, usar siempre `tipo_registro == 'agrupacion'`.** Sumar sin filtrar
cuenta dos veces: las listas internas ya están dentro de su agrupación, y
`positivo` y `total` son agregados.

## 6. Procedencia

Toda fila arrastra de dónde viene. Dos columnas, obligatorias:

- **`fuente`**: qué archivo u organismo la originó.
- **`recuento_tipo`**: `DEFINITIVO`, `PROVISORIO` o `NO DECLARADO`.

**Nunca se mezclan recuentos distintos en un mismo cálculo.** El provisorio y
el definitivo difieren alrededor de un 2 % en las fuerzas principales, lo
que basta para alterar una conclusión. Ver
[`NOTA_METODOLOGICA_2023.md`](NOTA_METODOLOGICA_2023.md).

## 7. Controles de consistencia

Todo parser valida antes de escribir, y **avisa en pantalla en cada corrida**:

1. Las agrupaciones suman el total de positivos.
2. Positivos + blancos + nulos + impugnados + recurridos = total de votantes.
3. La participación calculada sobre el padrón coincide con la declarada.
4. En PASO, las listas internas suman el total de su agrupación.

Un control que falla es un error de la base, no un detalle. Así se detectó
que los votos de La Libertad Avanza en Entre Ríos se contaban dos veces.

## 8. Forma de los archivos .xlsx

Un archivo por elección, en `salida/xlsx/`, nombrado
`<anio>_<instancia>_santa_fe_presidente.xlsx`.

Hay una tensión real entre "listo para visualizar" y "procesable por código".
Se resuelve **no eligiendo**: cada archivo trae las dos formas de la misma
información, y ninguna hoja mezcla ambos criterios.

| Hoja | Forma | Para qué |
|---|---|---|
| `Resumen` | una fila por elección | lectura humana rápida |
| `Resultados_ancho` | una fila por unidad, una columna por agrupación | unir con la capa geográfica y mapear |
| `Resultados_largo` | una fila por unidad × agrupación | `pandas`, `ggplot`, análisis |
| `Nomenclador` | una fila por unidad | cruzar con cartografía |
| `Metadatos` | clave-valor | procedencia, controles, advertencias |

Reglas que valen para **todas** las hojas de datos:

- **Fila 1 son los encabezados. Sin títulos, logos ni filas en blanco arriba.**
  `pd.read_excel(archivo, sheet_name='Resultados_largo')` tiene que funcionar
  sin argumentos extra.
- **Sin celdas combinadas** en las hojas de datos.
- **Una tabla rectangular por hoja**, sin bloques sueltos al costado.
- **Los porcentajes se guardan como fracción** (0.2526), con formato de
  celda `0.00%`. Así `0.25` es 25 % y no 25 veces.
- **Los identificadores son texto** (`circuito_id`, `distrito_id`), para no
  perder los ceros a la izquierda.
- **Los valores derivados se escriben como números, no como fórmulas.** Una
  fórmula escrita por `openpyxl` no lleva valor cacheado: hasta que una
  planilla de cálculo la abra y la evalúe, `pandas` la lee vacía. Como estos
  archivos existen para ser procesados por código, llevan el número ya
  calculado. **La reproducibilidad no la da la fórmula en la celda sino el
  script**: si un valor está mal, se corrige
  `scripts/generar_xlsx_por_eleccion.py` y se regenera todo.
- **Nombres de columna en minúscula, sin tildes ni espacios**, con guion
  bajo. Son nombres de variable, no títulos.

## 9. Comparabilidad entre años

Una serie temporal exige **tres condiciones**, no una:

1. **Etiquetas homologadas.** La misma fuerza escrita igual todos los años.
2. **Continuidad política declarada.** Qué se considera la misma corriente a
   lo largo del tiempo es una decisión de investigación y vive en
   `datos/referencia/homologacion_agrupaciones.csv`, editable, no en el
   código.
3. **Mismo universo geográfico.** El más fácil de pasar por alto y el que más
   daño hace: comparar la provincia entera de un año con 30 localidades de
   otro mide un cambio de recorte, no un cambio político.

La columna `universo` de `serie_homologada.csv` marca el recorte de cada
fila. **Filtrar por ella antes de agregar cualquier serie.** Ver
[`HOMOLOGACION.md`](HOMOLOGACION.md).

## 10. Cómo leerlos desde Python

```python
import pandas as pd

largo = pd.read_excel("salida/xlsx/2023_PASO_santa_fe_presidente.xlsx",
                      sheet_name="Resultados_largo",
                      dtype={"circuito_id": str, "distrito_id": str})

# Siempre filtrar por tipo_registro antes de sumar.
votos = largo[largo.tipo_registro == "agrupacion"]
por_agrupacion = votos.groupby("agrupacion").votos.sum().sort_values(ascending=False)
```

Para unir con cartografía, usar `Resultados_ancho` y cruzar por
`circuito_id`, recordando normalizar los ceros a la izquierda de ambos lados.

## 11. Qué hacer al agregar una fuente nueva

1. Guardar el original en `datos/crudos/<nivel>/`, sin editarlo.
2. Renombrarlo `<anio>_<instancia>_<...>` para que el contenido se lea en el
   nombre.
3. Escribir o extender un parser en `scripts/`, con sus controles.
4. Declarar `fuente` y `recuento_tipo` en cada fila.
5. Correr los controles y no seguir hasta que den limpio.
6. Anotar la procedencia en `datos/INVENTARIO.md`.
