# Diccionario de datos

La base vive en `data/processed/`: un CSV por tabla y `santafe_electoral.db`
(SQLite) que los reúne. El esquema autoritativo es `src/esquema.sql`.

## `hechos_votos` — tabla de hechos

Una fila por **elección × localidad × tipo de voto × agrupación**.

| campo | tipo | descripción |
|---|---|---|
| `eleccion_id` | texto | Instancia, p. ej. `2015-BALLOTAGE`. FK a `dim_eleccion`. |
| `anio` | entero | Año de la elección (redundante, para consultas directas). |
| `instancia` | texto | `PASO`, `GENERAL` o `BALLOTAGE`. |
| `departamento_id` | texto | Clave normalizada, p. ej. `LAS_COLONIAS`. |
| `departamento` | texto | Nombre para mostrar, con acentos. |
| `localidad_id` | texto | Clave normalizada. FK a `dim_localidad`. |
| `localidad` | texto | Nombre para mostrar. |
| `tipo_voto` | texto | `POSITIVO`, `BLANCO`, `NULO`, `RECURRIDO`, `IMPUGNADO`. |
| `agrupacion_key` | texto | Clave normalizada de la agrupación. **Solo** si `tipo_voto = POSITIVO`; si no, vacío. |
| `agrupacion_nombre_fuente` | texto | La etiqueta tal como la escribe la fuente, sin retocar. |
| `formula` | texto | Fórmula presidencial, cuando la fuente publica candidatos (2003 y 2007). |
| `votos` | entero | **Siempre absoluto.** Nunca un porcentaje. |
| `fuente_id` | texto | FK a `fuentes`. |

Dos reglas que la base hace cumplir por restricción, no por convención:

- Un voto no positivo nunca tiene agrupación, y uno positivo siempre la tiene.
- `votos` nunca es negativo.

**Cómo no contar dos veces**: los votos positivos están desagregados por
agrupación; el total de positivos de una localidad es su suma, y no existe una
fila `POSITIVO` agregada. El total declarado por la fuente se usa para validar
esa suma, y si no coincide queda registrado en `incidencias`.

## Dimensiones

### `dim_eleccion`
Las 12 instancias del período, estén cargadas o no. `cargada` vale 1 si ya tiene
datos: permite ver el avance sin salir de la base. `nota` guarda la advertencia
de comparabilidad (p. ej. que un ballotage tiene solo dos fórmulas).

### `dim_departamento`
Los 19 departamentos con su **código oficial de la DINE** (1 = La Capital … 19 =
San Lorenzo), tomado del nomenclador `AmbitosElectorales`. El código importa por
dos razones: es una clave estable que no depende de cómo se escriba el nombre, y
es la que permite unir con las capas geográficas para los mapas.

### `dim_localidad`
`localidad_id`, nombre, departamento. Es el ancla geográfica de la serie.

### `dim_circuito`
Una fila por `(circuito_id, eleccion_id)`: el nomenclador **versionado por
elección**. Así conviven la numeración previa y la renumeración de 2023 sin
romper la continuidad de las localidades.

### `dim_agrupacion`
Una fila por `(agrupacion_key, eleccion_id)`. `etiqueta_tipo` dice si la fuente
publica `AGRUPACION` o `FORMULA` en ese año.

`espacio_politico` **está vacía a propósito**. Agrupar FPV / Unidad Ciudadana /
Frente de Todos / Unión por la Patria bajo una misma etiqueta, o Cambiemos con
Juntos por el Cambio, es una decisión interpretativa del trabajo, no un dato de
la fuente. Se define y documenta en la etapa siguiente; hasta entonces la columna
queda vacía y nadie puede confundir el criterio con un hecho.

## Tablas de apoyo

### `padron`
`mesas` y `electores` por elección y localidad. Es el denominador disponible para
calcular participación.

### `fuentes`
Registro de trazabilidad: archivo, organismo, archivo de origen, unidad original
(mesa / circuito / localidad), carácter del recuento, cobertura declarada, fecha
de procesamiento y `sha256`. Toda fila de hechos apunta acá.

### `control_totales` y `control_padron`
Los totales que la DINE publica **agregados por distrito**: una fila por
elección, ámbito (`PAIS` o `PROVINCIA`), tipo de voto y agrupación, más el padrón
y los votantes declarados.

No forman parte de la serie y nunca se mezclan con `hechos_votos`: son el patrón
contra el cual se contrasta lo que arroja la base. Mientras la cobertura por
localidad sea parcial, el validador informa qué porcentaje del total provincial
ya está cargado; si alguna vez la base supera ese total, eso sí es un error.

Estas tablas ya sirven por sí solas para leer la serie provincial: padrón,
participación y voto por agrupación en Santa Fe para 8 de las 12 instancias.

### `incidencias`
Descuadres detectados durante la ingesta, con valor esperado, obtenido y
diferencia. No se corrigen automáticamente: se muestran.

## Vista `v_totales_localidad`

Totales por elección y localidad (positivos, blancos, nulos, recurridos,
impugnados, votantes) con `electores` y `mesas` al lado. Es el punto de partida
para calcular participación y porcentajes, eligiendo el denominador de forma
explícita.

```sql
-- Participación sobre electores, ballotage 2023, por departamento
SELECT departamento,
       SUM(votantes) * 100.0 / SUM(electores) AS participacion
FROM v_totales_localidad
WHERE eleccion_id = '2023-BALLOTAGE'
GROUP BY departamento
ORDER BY participacion DESC;
```
