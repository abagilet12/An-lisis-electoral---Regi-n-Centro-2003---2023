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

## Recibido y registrado

### PASO 2023 — escrutinio provisorio (parcial)

`data/raw/2023_paso_diccionarios/`, con `sha256` de cada archivo en su manifiesto.

| archivo | contenido |
|---|---|
| `agrupaciones.csv` | agrupaciones por categoría y distrito |
| `listas.csv` | listas internas de cada agrupación |
| `categorias.csv` | 1 = Presidente y Vice |
| `distritos.csv` | los 24 distritos |
| `establecimientos.csv` | 17.430 establecimientos del país, 1.429 de Santa Fe |
| `secciones.csv` | las secciones (departamentos) de los 24 distritos |
| `municipios.csv` | municipios — **solo de Buenos Aires, Catamarca y Santa Cruz** |
| `mesas-totales.csv` | totales por mesa: participación, blancos, nulos, recurridos |

Son las **PASO 2023**: la confirmación es que Juntos por el Cambio y Unión por la
Patria aparecen con dos listas internas cada una, cosa que solo ocurre en
primarias. En Santa Fe hay 15 agrupaciones y 27 listas presidenciales.

`mesas-totales.csv` sí trae datos de Santa Fe, y buenos: **8.332 mesas, 523
circuitos, los 19 departamentos**, con 2.776.689 habilitados y 1.885.494
votantes (67,9% de participación, coherente con la PASO 2023). Con eso ya se
puede armar participación, blancos y nulos por departamento y por circuito.

**Lo que falta es el archivo de votos por agrupación.** `mesas-totales.csv` da
los totales de cada mesa pero no cuántos votos sacó cada fuerza. Sin ese archivo
la instancia queda a medias: hay denominador, no hay reparto.

Es un corte del **escrutinio provisorio de la noche de la elección** (marca de
tiempo 2023-08-13/14), todavía más preliminar que los ZIP "PROVISORIOS" del
portal. Queda registrado en el manifiesto.

Dos cosas que sí aportan desde ya:

- **El universo completo de circuitos de Santa Fe**: 523 circuitos con su
  departamento, contra los 30 que teníamos mapeados. Es la lista contra la cual
  se va a medir cuánto cubre el nomenclador.
- **Los nombres de los establecimientos** (escuelas), que suelen contener la
  localidad y sirven como insumo para construir el mapeo circuito → localidad.
  Es un método aproximado y habrá que validarlo, pero es un punto de partida
  para 523 circuitos donde hoy no hay nada.

### Un hallazgo negativo que conviene tener claro

`municipioId` viene vacío en los 1.429 establecimientos de Santa Fe y en las
8.332 mesas. Y `municipios.csv` lo explica: **solo define municipios para Buenos
Aires, Catamarca y Santa Cruz. Santa Fe no tiene ninguno.**

Es decir: **el dataset de la DINE no trae localidad para Santa Fe por ningún
lado.** La desagregación por localidad no va a salir de esta fuente, por más
archivos que sumemos. Tiene que venir de otro lado:

1. El nomenclador de los archivos `Votos por Localidad` (30 circuitos, ya
   mapeados en etapas previas del proyecto).
2. El GeoJSON de circuitos, si trae nombre de localidad.
3. Los nombres de los establecimientos, como método aproximado.

Conviene saberlo ahora y no después de juntar todo: **el objetivo "por
localidad" depende enteramente de construir ese mapeo a mano o por cruce
geográfico.** El nivel departamento, en cambio, está garantizado.

⚠️ **Riesgo registrado**: el `circuitoId` viene acá con cinco dígitos (`00010`),
mientras que en los resultados de 2011 aparece como `0557 ` con espacio al final
y en el nomenclador de los derivados como `0055` o `0134A`. Son formatos
distintos del mismo identificador. Unificarlos es condición para cruzar
circuitos entre años, y hay que resolverlo con cuidado: un error acá asigna
votos a la localidad equivocada.

### Votos por Localidad — 5 de 10 recibidos

Ballotage 2015, PASO 2019, Generales 2019, Generales 2023 y Segunda Vuelta 2023.
Los cinco íntegros y los cinco los lee el ingestor sin una sola incidencia: en
las 150 combinaciones de localidad y elección, el total de positivos declarado
coincide exactamente con la suma por agrupación. Es un buen indicio de la
calidad del trabajo previo.

Faltan cinco: **2007, PASO 2011, Generales 2011, PASO 2015 y Generales 2015**.

### La cadena de identificadores de circuito, resuelta

Estos archivos permitieron cerrar el problema de normalización que estaba
anotado como riesgo. La renumeración de Santa Fe en 2023 **sigue una regla
determinística**, verificada sobre las 30 localidades que aparecen en ambos
períodos:

| localidad | 2015 y 2019 | 2023 | establecimientos.csv |
|---|---|---|---|
| Esperanza | `0055` | `0550` | `00550` |
| Ataliva | `0121` | `1210` | `01210` |
| Cañada Rosquín | `0161` | `1610` | `01610` |
| Frontera | `0134A` | `1345` | `01345` |

La regla: **el código anterior se corre un dígito a la izquierda** (equivale a
multiplicarlo por diez), y el archivo de establecimientos usa el mismo código
con un cero adelante. Verificado: los 11 códigos probados aparecen en los 523
circuitos de 2023, sin excepción.

Los sub-circuitos con letra siguen la misma lógica y la letra pasa a dígito
(`0134A` → `1345`). Hay un solo caso observado, así que **esa parte de la regla
no está confirmada** y hay que validarla cuando aparezcan más sub-circuitos.
De los 523 circuitos de 2023, 384 terminan en cero y 139 no: esos 139 son
sub-circuitos y son los que pueden dar problemas.

Consecuencia práctica: cualquier mapeo circuito → localidad que construyamos se
puede expresar en una forma canónica y aplicar a toda la serie, sin rehacerlo
por año. Eso vale tanto para los 30 circuitos que ya tenemos como para los que
sumemos después.

## Prioridad 1 — Las dos PASO con URL rota

Son las más fáciles: el dataset existe en el catálogo de datos.gob.ar, pero el
enlace devuelve 404. Ambos cuelgan de la ruta `/dine-resultados/`.

- **PASO 2015**: `2015-PROVISORIOS_PASO.zip`
- **PASO 2023**: `2023-PROVISORIOS_PASO.zip` — de este ya llegaron los
  diccionarios; falta el archivo de resultados por mesa.

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

## Prioridad 4 — Los 5 archivos `Votos por Localidad` que faltan

**2007, PASO 2011, Generales 2011, PASO 2015 y Generales 2015.** Están en tu
Drive (`Datos electorales 2007 - 2023`). **Bajaron de prioridad** como fuente de
resultados:
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
