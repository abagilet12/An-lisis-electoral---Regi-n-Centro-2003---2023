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

## El nivel de circuito SÍ funciona (corrección)

Una versión anterior de este documento concluía que el nivel de circuito era
inaccesible. **Era un error**: se estaban probando los códigos del
nomenclador de padrón (`1210` para Ataliva), que no son los que usa la API.

Los códigos correctos son los del archivo por mesa de la DINE: cinco dígitos
con ceros a la izquierda, `00115`. Con esos, `circuitoId` responde, y ni
siquiera hace falta pasar `seccionId`:

```
?anioEleccion=2023&tipoRecuento=1&tipoEleccion=1&categoriaId=1
&distritoId=21&circuitoId=00115
→ 29 mesas, 9.856 electores
```

Como no hay endpoint que liste los ámbitos, los códigos se descubren por
barrido del espacio de ids. Verificado: barriendo 1-1200 en la general 2023
aparecen 129 circuitos, **todos reales** —coinciden uno a uno con los del
archivo por mesa, sin falsos positivos—. Los 394 restantes están por encima
de ese rango.

### Y dentro de 2023, tampoco para el balotaje

Muestreando 999 códigos sobre todo el espacio de ids, **en la misma corrida**:

| Elección 2023 | Circuitos hallados |
|---|---:|
| General | 380 |
| Segunda vuelta | **0** |

Probado además con los 523 códigos reales de la general y pasando
`seccionId` como padre: nada. El circuito no está publicado para la segunda
vuelta. El balotaje sí responde a nivel departamento, que es lo que la base
ya tiene.

### Solo para 2023, y no para todas sus instancias

Muestreando 999 códigos repartidos sobre todo el espacio de ids:

| Elección | Circuitos hallados |
|---|---:|
| 2023 General | 384 |
| 2019 General | **0** |
| 2015 General | **0** |

Se probó además pasando `seccionId` como padre, por si el circuito lo
requiriera en esos años: barrido de 1.499 códigos dentro de la sección 1 de
2019, cero resultados. **No es un problema de descubrir códigos: el dato no
está publicado a nivel circuito antes de 2023.**

Y para 2023 ese nivel ya lo tenemos del archivo por mesa, así que la API no
agrega nada ahí.

## Qué aporta realmente esta API al proyecto

El **nivel de departamento para 2011-2019**, que hoy falta en la base:

| Elección | Departamentos | Mesas (suma) | Mesas (provincia) | ¿Cierra? |
|---|---:|---:|---:|---|
| 2015 General | 18 de 19 | 7.718 | 7.852 | No, faltan 134 |
| 2019 General | **19 de 19** | 8.111 | 8.111 | **Sí, exacto** |
| 2023 General | 19 de 19 | 8.332 | — | Sí |

2019 es el caso limpio. 2015 queda 1,7 % corto. 2011 es claramente parcial y
además su agregado distrital está roto.

`notebooks/extraccion_api_dine.ipynb` automatiza la recolección. Son unas
200 consultas por elección, cuestión de segundos: no hace falta barrer
circuitos, porque ya se sabe que no existen antes de 2023.

## Cobertura real por año

A nivel distrito, comprobado contra lo que se sabe de la provincia:

| Año | Mesas que devuelve | ¿Completo? |
|---|---:|---|
| 2011 PASO | 616 | **No**, el agregado distrital está roto |
| 2011 General | 356 | **No**, ídem |
| 2015 General | 7.852 | Sí |
| 2019 General | 8.111 | Sí |
| 2023 General | 8.332 | Sí, coincide exacto con el definitivo de la JNE |

En las elecciones donde el agregado distrital falla hay que sumar las partes
(secciones o circuitos) en vez de confiar en el total.

## Qué resuelve y qué no

| Necesidad | ¿La API la cubre? |
|---|---|
| PASO 2023 por departamento | Sí, pero provisional |
| General 2003 por localidad | **No** — no hay datos previos a 2011 |
| Serie 2011-2019 por departamento | Sí, provisional, remapeando ids por año |
| Desagregación por circuito | **Sí**, con los códigos de 5 dígitos de la DINE |
| Desagregación a localidad | Solo con el nomenclador circuito→localidad, relevado aparte |

Para el nivel circuito, que es el que permite reconstruir localidades, sigue
siendo más directa la descarga masiva por mesa de
`resultados.mininterior.gob.ar` (los `presentacionDeResultados*.csv` con los
que ya se construyeron los archivos por localidad), que además trae el
escrutinio definitivo.
