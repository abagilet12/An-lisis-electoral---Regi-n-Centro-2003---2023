# Plan de recolección

Qué falta conseguir, ordenado por prioridad. Se deriva directamente del encuadre
([`00-encuadre.md`](00-encuadre.md)): 12 instancias presidenciales, 2003–2023,
19 departamentos de Santa Fe, desagregado por departamento y localidad.

**Antes de buscar nada, revisá la columna "Estado": ya tenemos 8 de las 12
instancias a nivel mesa.** No hace falta recolectarlas de nuevo.

## Estado por instancia

| # | Instancia | Nivel mesa (la serie) | Total provincial (control) |
|---|---|---|---|
| 1 | 2003 general | ❌ **falta** | ✅ |
| 2 | 2007 general | ❌ **falta** | ✅ |
| 3 | 2011 PASO | ✅ portal | ✅ |
| 4 | 2011 general | ✅ portal | ✅ |
| 5 | 2015 PASO | ❌ **falta** (URL rota) | ✅ |
| 6 | 2015 general | ✅ portal | ✅ |
| 7 | 2015 ballotage | ✅ portal | ✅ |
| 8 | 2019 PASO | ✅ portal | ❌ falta (solo total país) |
| 9 | 2019 general | ✅ portal | ✅ |
| 10 | 2023 PASO | ❌ **falta** (URL rota) | ❌ falta |
| 11 | 2023 general | ✅ portal | ❌ falta |
| 12 | 2023 ballotage | ✅ portal | ❌ falta |

**Faltan 4 instancias a nivel mesa: 2003, 2007, PASO 2015 y PASO 2023.**

## Prioridad 1 — Las dos PASO con URL rota

Son las más fáciles: el dataset existe en el catálogo de datos.gob.ar, pero el
enlace devuelve 404. Ambos cuelgan de la ruta `/dine-resultados/`.

- **PASO 2015**: `2015-PROVISORIOS_PASO.zip`
- **PASO 2023**: `2023-PROVISORIOS_PASO.zip`

Dónde buscarlas: la ficha del dataset en datos.gob.ar (puede tener un enlace
actualizado que la API no refleja), o el sitio de la DINE en argentina.gob.ar.
Deben pesar entre 25 y 40 MB y traer un `ResultadosElectorales.csv` adentro.

## Prioridad 2 — 2003 y 2007 a nivel circuito

Son anteriores a la política de datos abiertos, así que no están en el portal.
Es la parte más difícil de la serie y la que decide si el análisis arranca en
2003 con la misma resolución que el resto.

- **2007**: `Argentina07.mdb`, el archivo que ya usaste para construir el
  derivado de 2007. Es el que tenés a mano y resuelve la instancia entera.
- **2003**: sin fuente identificada. Alternativas a explorar, en orden:
  1. Tribunal Electoral de la Provincia de Santa Fe.
  2. Archivo histórico de la DINE.
  3. Atlas Electoral de Andy Tow (dato derivado, citar como tal).
  4. Pedido formal a la Cámara Nacional Electoral.

Si para 2003 solo aparece dato por **departamento** y no por circuito, sirve
igual: se carga declarándolo como serie de menor resolución. Lo que no se hace
es mezclarlo en silencio con el resto.

## Prioridad 3 — Escrutinios definitivos

Todo lo descargado del portal es **recuento provisorio**. Los definitivos están
en `padron.gob.ar/publica`, que no se automatiza: sus condiciones de uso
restringen la consulta a pedidos individuales de ciudadanos.

Vía correcta para volumen: pedido a la Cámara Nacional Electoral,
`cnelectoral.datosabiertos@pjn.gov.ar`. Un proyecto CAI+D con aval institucional
tiene con qué pedirlo, y conviene hacerlo temprano porque puede demorar.

Mientras tanto la serie se arma con provisorios, declarado en cada fila.

## Prioridad 4 — Los 10 archivos `Votos por Localidad`

Están en tu Drive (`Datos electorales 2007 - 2023`). **Bajaron de prioridad**:
los archivos del portal cubren las mismas instancias con más alcance (los 19
departamentos en vez de 3).

Siguen valiendo por dos razones, las dos de control:

1. Traen el **nomenclador circuito → localidad** de 30 circuitos, que es la
   semilla del mapeo que hace falta para desagregar por localidad.
2. Permiten **verificar que el pipeline reproduce el trabajo hecho a mano**: si
   procesamos el archivo del portal y da lo mismo, localidad por localidad, que
   el derivado de esa instancia, el pipeline queda validado contra trabajo
   humano. Es la mejor prueba disponible.

## Prioridad 5 — Capas geográficas para el mapa

Lo que se necesita para el mapa final, en orden de importancia:

1. **Circuitos electorales de Santa Fe** (GeoJSON). Es la unidad que permite
   armar localidades.
2. **Departamentos de Santa Fe** (ya hay capas del IGN en tu Drive).
3. **Localidades**, si existiera una capa oficial.

### Qué necesita traer el GeoJSON para que sirva

Esto es lo que decide si el archivo se puede cruzar con los datos o no:

- **Un identificador de circuito en las propiedades de cada polígono**, que se
  corresponda con el `circuito_id` de la DINE. Es el requisito crítico: sin él,
  el mapa es un dibujo que no se puede unir con los votos.
- **Coordenadas en WGS84** (EPSG:4326). Si viene en otro sistema, hace falta
  saber cuál.
- **El año o la versión del circuito**: Santa Fe renumeró circuitos en 2023, así
  que un mapa de circuitos sirve para unas elecciones y no para otras. Saber a
  qué momento corresponde es indispensable.

Si el archivo no trae identificador de circuito, avisá antes de que lo
procesemos: se puede resolver por cruce espacial o por nombre, pero son métodos
aproximados que hay que documentar como tales.

## Cómo pasar los archivos

**Adjuntos acá en el chat**, no por Drive: los binarios de Drive no se pueden
reconstruir intactos (comprobado, se corrompen). Los del chat llegaron bien.

A medida que lleguen los registro en
[`02-manifiesto-fuentes.md`](02-manifiesto-fuentes.md) con su `sha256`, y
actualizo la tabla de estado de este documento.
