# API de Publicación de Resultados Electorales (DINE)

Evaluación hecha el 2026-09-17 sobre el spec
`api-publicacion-resultados-electorales.yaml`, contrastada con consultas
reales a la API.

- Base: `https://resultados.mininterior.gob.ar/api`
- Endpoint único documentado: `GET /resultados/getResultados`
- Cliente: `scripts/cliente_api_dine.py`

## Autenticación: no hace falta

El spec declara `bearer_auth` (JWT) y el texto dice que "puede requerirse".
En la práctica, las consultas de resultados históricos responden HTTP 200 sin
credenciales. No hay que gestionar ningún token.

## Parámetros útiles

| Parámetro | Valor para este proyecto |
|---|---|
| `categoriaId` | `1` = Presidente (verificado: 35.405.013 electores nacionales en 2023) |
| `distritoId` | `21` = Santa Fe (verificado: 2.827.794 electores, 8.332 mesas en la general 2023) |
| `tipoEleccion` | `1` = PASO, `2` = Generales, `3` = Segunda vuelta |
| `tipoRecuento` | `1` = Recuento provisional (es el único disponible) |
| `seccionId` | `1`-`19` = los 19 departamentos de Santa Fe |
| `circuitoId` | existe, pero no se logró determinar el esquema de códigos |

La respuesta trae votos por agrupación —con desglose de listas internas en
las PASO—, más nulos, blancos, recurridos/comando/impugnados, electores,
votantes y participación.

## Las cuatro limitaciones que importan

### 1. No hay datos anteriores a 2011

Verificado consultando año por año: 2003 y 2007 devuelven vacío. **La API no
resuelve el hueco de 2003**, que sigue necesitando otra fuente.

### 2. Devuelve el recuento provisional, no el escrutinio definitivo

Comparando la PASO 2023 de Santa Fe que da la API contra el escrutinio
definitivo de la Justicia Nacional Electoral que ya está en el repo:

| Agrupación | Definitivo (JNE) | Provisional (API) | Diferencia |
|---|---:|---:|---:|
| La Libertad Avanza | 661.659 | 646.315 | −15.344 |
| Juntos por el Cambio | 591.233 | 579.867 | −11.366 |
| Unión por la Patria | 394.908 | 386.865 | −8.043 |
| Hacemos por Nuestro País | 69.149 | 67.563 | −1.586 |

Son entre 2 y 2,3 % menos en las tres fuerzas principales. **No se pueden
mezclar ambas fuentes en una misma serie.** Para un trabajo académico
conviene el escrutinio definitivo; la API sirve para explorar y para
completar lo que no esté disponible de otro modo, dejándolo declarado.

### 3. Los ids de ámbito no son estables entre años

`seccionId=1` devuelve 102 mesas en 2011 y 1.330 en 2023: el mapeo
id→departamento cambia. Hay que reconstruir la correspondencia por año antes
de comparar series, nunca asumir que un id significa lo mismo siempre.

### 4. Las PASO a nivel distrito devuelven un total parcial

Consultar `distritoId=21` sin `seccionId` en las PASO 2023 devuelve 3.050
mesas en lugar de 8.332. Sumando las 19 secciones el total cierra correcto.
Por eso `total_provincial()` recorre las secciones en vez de pedir el
distrito. Es un comportamiento anómalo de la API, no un dato faltante.

## Otros endpoints no documentados en el spec

Extraídos del bundle JavaScript de la aplicación web:

| Endpoint | Estado |
|---|---|
| `GET /api/menu/periodos` | Funciona. Devuelve `[2025, 2023, 2021, 2019, 2017, 2015, 2013, 2011]`, que confirma el piso de 2011 |
| `GET /api/menu` | Funciona. Lista las elecciones con su `IdEleccion` y fecha |
| `GET /api/resultado/totalizadocsv` | Existe pero inutilizable: responde 409 pidiendo `año, recuentoId, eleccionId, categoriaId` y sigue rechazando esos mismos parámetros en todas las codificaciones probadas (UTF-8, latin-1, sin eñe, mayúsculas) |
| `GET /api/menu/distritos` | Responde 409 `error al obtener el menu` con cualquier combinación |

El botón "Descargar CSV" de la web genera el archivo en el navegador a partir
de las respuestas de la API: no hay un archivo servido que se pueda pedir.

## El nivel de circuito sigue cerrado

`circuitoId` es un parámetro válido del endpoint, pero no se logró determinar
su esquema de códigos. Probado sin éxito: los códigos del nomenclador de
padrón (1210 para Ataliva) crudos, con relleno a 6 y a 7 dígitos, barridos
contra las 19 secciones, e ids secuenciales. El id parece ser interno del
Sistema de Recuento, como ya advierte el spec para `idAgrupacion`.

Sin el árbol de ámbitos —que `menu/distritos` no entrega— no hay forma de
descubrirlos desde la API. **Para llegar a localidad sigue haciendo falta el
archivo por mesa.**

## Qué resuelve y qué no

| Necesidad | ¿La API la cubre? |
|---|---|
| PASO 2023 por departamento | Sí, pero provisional |
| General 2003 por localidad | **No** — no hay datos previos a 2011 |
| Serie 2011-2019 por departamento | Sí, provisional, remapeando ids por año |
| Desagregación por circuito → localidad | **No**, ver arriba |

Para el nivel circuito, que es el que permite reconstruir localidades, sigue
siendo más directa la descarga masiva por mesa de
`resultados.mininterior.gob.ar` (los `presentacionDeResultados*.csv` con los
que ya se construyeron los archivos por localidad), que además trae el
escrutinio definitivo.
