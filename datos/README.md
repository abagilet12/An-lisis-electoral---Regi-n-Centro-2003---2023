# Datos — Análisis electoral Región Centro 2003-2023

Región Centro = Córdoba (distrito 04), Entre Ríos (08) y Santa Fe (21).

## Estructura

```
datos/
  crudos/<año>/     archivos originales, sin modificar
  procesados/       CSV normalizados, generados por scripts/
```

Los archivos crudos se renombran a
`<año>_<instancia>_DIST<nn>_<provincia>_<cargo>.<ext>` para que el origen sea
legible; el contenido no se toca nunca. El código de distrito del nombre es la
fuente de verdad, porque el encabezado de algunos `.xls` viene truncado
(p. ej. `Distrito: C` por Córdoba en el balotaje).

## Formato de salida: CSV tidy, una fila por observación

`datos/procesados/resultados.csv`

| columna | descripción |
|---|---|
| `anio`, `instancia`, `fecha`, `cargo` | `instancia` ∈ PASO / GENERAL / BALOTAJE; `fecha` ISO |
| `distrito_id`, `distrito` | código CNE de dos dígitos y nombre |
| `seccion_id`, `seccion`, `circuito_id`, `circuito`, `mesa_id` | vacías cuando el dato es distrital; se llenan con fuentes más finas |
| `agrupacion_id`, `agrupacion` | alianza / frente |
| `lista_id`, `lista` | lista interna (solo PASO) |
| `tipo_registro` | `agrupacion`, `lista`, `nulos`, `blancos`, `recurridos`, `impugnados`, `total` |
| `votos` | entero |
| `pct_general`, `pct_validos`, `pct_afirmativos` | porcentajes tal como los publica la JNE |
| `pct_interna` | peso de la lista dentro de su agrupación (PASO) |
| `archivo_origen` | trazabilidad hasta el archivo crudo |

`datos/procesados/metadatos.csv` — padrón, mesas y participación, en formato
largo (`concepto`, `categoria` ∈ inscriptos/mesas/participacion, `valor`), porque
las categorías varían entre elecciones (residentes en el exterior aparecen en
generales pero no en PASO, etc.).

### Por qué este formato

- **Largo y no ancho**: la oferta electoral cambia en cada elección. Una columna
  por partido obligaría a rehacer el esquema en cada acto; con formato largo
  solo se agregan filas.
- **Un único archivo por tabla**, no uno por elección: los cortes
  (año × provincia × instancia) salen filtrando, no uniendo.
- **Votos y agregados en la misma tabla**, distinguidos por `tipo_registro`:
  permite reconstruir el total y validar contra la fila `total`.
- **Columnas geográficas siempre presentes**: cuando incorporemos datos por
  circuito o mesa, el esquema no cambia — solo dejan de estar vacías.
- **CSV plano UTF-8**: legible por pandas, R, QGIS, Excel y por `git diff`.

## Uso

```bash
pip install xlrd
python3 scripts/parse_escrutinio_zona.py
```

El script valida que la suma de agrupaciones + nulos + blancos + recurridos +
impugnados coincida con la fila `TOTALES` de cada archivo, y avisa si no.

## Inventario

Cubierto (nivel distrito, cargo Presidente y Vice):

| Año | Instancia | Córdoba | Entre Ríos | Santa Fe |
|---|---|---|---|---|
| 2023 | PASO | ✓ | ✓ | ✓ |
| 2023 | General | ✓ | ✓ | ✓ |
| 2023 | Balotaje | ✓ | ✓ | ✓ |

2023 está completo para las tres provincias. Falta 2003-2019.

## Irregularidades de la fuente

La JNE no publica los tres distritos con el mismo formato. Lo detectado hasta
ahora, y resuelto en el parser:

- **Distrito truncado**: el balotaje de Córdoba trae `Distrito: C`. El código
  del nombre de archivo manda sobre el encabezado.
- **Código de lista interna**: en Córdoba va en la primera columna (`20"A"`);
  en Entre Ríos y Santa Fe esa columna repite el código de la agrupación y el
  código de lista viene como prefijo del nombre (`A - DEMOS`, `1A TIERRA,
  TECHO Y TRABAJO`). El parser lo normaliza a la letra en `lista_id`.
- **Códigos que no encadenan**: en el PASO de Entre Ríos la lista de La
  Libertad Avanza figura con código `503` dentro de la agrupación `135`. Por
  eso la pertenencia lista→agrupación se decide por la estructura del bloque
  (cabecera sin votos … fila `TOTAL`), nunca por el prefijo del código.
- **Participación como texto**: viene `75.09%`, y la etiqueta cambia entre
  `Votantes` y `Asistencia` según el archivo.
- **Nombres de agrupación no homologados**: la misma fuerza aparece como
  `UNION POR LA PATRIA`, `UNIÓN POR LA PATRIA` y `UNION POR LA PATRIA (SERGIO
  MASSA - AGUSTIN ROSSI)` según distrito e instancia. Pendiente: tabla de
  homologación para poder comparar entre años.

## Nota sobre la granularidad

Los `.xls` de "Consulta de Escrutinio por Zona" de la Justicia Nacional
Electoral son agregados **del distrito entero**: no traen sección, circuito ni
mesa. Para trabajar por circuito hace falta la otra fuente: los datasets de
escrutinio definitivo de la DINE (`resultados_<año>.csv`), que vienen a nivel
mesa con `seccion_id` y `circuito_id`, y se agregan a circuito sumando.
Ese formato entra en este mismo esquema sin cambios.
