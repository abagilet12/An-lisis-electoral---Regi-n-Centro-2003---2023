# Fuentes de resultados: Santa Fe, categoría Presidente, 2003-2023

Qué fuentes hay, qué cubre cada una y con cuál conviene trabajar. Los partidos y
frentes se tratan con **el nombre oficial de la etiqueta tal como figura en cada
elección**, sin agruparlos ni analizar su composición.

## Fuentes disponibles

| Fuente | Cobertura | Recuento | Archivo |
|---|---|---|---|
| Excel de la DINE (resultados por distrito) | Generales 2003, 2007, 2011, 2015, 2019; PASO 2011 y 2015; balotaje 2015. Provincia y país | Definitivo | Se descarga con `scripts/construir_top3.py` |
| CSV de mesas y API de la DINE | Generales, PASO y balotaje 2023 | Provisorio | Ídem |
| Base propia (PolAr / DINE) | Las 12 instancias, hasta circuito | Provisorio | `datos/procesados/serie_homologada.csv` (rama de datos) |
| Base recibida 2011-2023 | 10 de las 12 instancias, solo provincia | Provisorio | `datos/crudos/otras_fuentes/` (ver `VALIDACION_BASE_2011_2023.md`) |
| Registro de candidaturas presidenciales de la DINE | Fórmula de cada etiqueta en las generales 1983-2023 | Oficial | `datos/crudos/dine_candidaturas/` y `datos/referencia/formulas_presidenciales_1983_2023.csv` |
| Registro de partidos (UEEDA, 30/09/2026) | Nombre legal, sigla y vigencia de los partidos | Oficial | `datos/crudos/dine_registro_partidos/` |

## Con qué trabajar

- **Totales provinciales:** el Excel oficial de la DINE cuando existe (definitivo).
  Para 2019 PASO y todo 2023, solo hay provisorio.
- **Detalle por departamento, circuito y localidad:** la base propia.
- **Diferencia entre ambos recuentos:** entre 0,2 % y 1,4 % del ganador (ver
  `VALIDACION_BASE_2011_2023.md`). No se mezclan en una misma serie.
- **Faltan** los resultados definitivos desagregados por distrito de las PASO 2019, las
  PASO 2023 y el balotaje 2023.

## Los tres primeros de cada instancia

`datos/referencia/top3_por_eleccion.csv` tiene el top 3 de Santa Fe y del país, con
la etiqueta tal cual la fuente y el porcentaje sobre votos positivos. Se regenera con
`scripts/construir_top3.py`.

Notas para leerlo:

- Los puestos de la base propia coinciden con los del Excel oficial en las doce
  instancias; los porcentajes difieren en décimas.
- En 2003 la diferencia entre el primero y el segundo en Santa Fe es de 1.801 votos
  (425.886 contra 424.085, definitivo).
- En 2019 General, Juntos por el Cambio gana en Santa Fe (43,49 %) y el Frente de
  Todos en el país.

## Nombres de las etiquetas

La misma etiqueta se escribe distinto según la fuente (por ejemplo «Concertación UNA»
en la base propia y «Alianza Concertación para una Nación Avanzada» en la DINE). Para
mostrar resultados se usa el nombre oficial del Excel de la DINE; las variantes quedan
en `top3_por_eleccion.csv` (columna `etiqueta_tal_cual`).

## Pestañas «Elecciones» y «Partidos» del tablero

`salida/voto_santafesino.html` tiene dos pestañas con el resultado de cada partido por
etiqueta oficial, hasta el nivel de circuito.

- **Elecciones:** una ficha por instancia, con mapa por departamento o circuito (un clic
  selecciona la unidad), tabla de resultados y participación, blancos y nulos. En el total
  provincial se muestra al lado el resultado definitivo de la DINE cuando existe.
- **Partidos:** una ficha por nombre oficial, con su evolución en las doce instancias,
  la tabla de nombres y resultados, el mapa de intensidad y el ranking por departamento.
  Si el partido cambió de nombre, la ficha ofrece un vínculo a la etiqueta anterior o
  siguiente con su fuente. Es una ayuda de navegación, no una afirmación de identidad.

**Cómo se regenera**

1. `python3 scripts/construir_datos_fichas.py --proc <datos procesados de la rama de datos>`
   genera `salida/datos_fichas.json` (resultados por circuito y etiqueta).
2. `python3 scripts/agregar_pestanas.py` inserta (o reemplaza) las pestañas en el HTML con
   las plantillas de `scripts/plantillas/`.

**Cosas que conviene saber**

- Departamento y provincia son la suma de circuitos, con recuento provisorio. El total
  provincial definitivo de la DINE se agrega como referencia.
- En 2011 PASO, tres partidos (Del Campo Popular, Movimiento de Acción Vecinal y Proyecto Sur)
  solo tienen total provincial, tomado de la base recibida: no tienen detalle territorial.
- En 2007, cuatro filas de la base que corresponden a un mismo frente de la DINE (El Movimiento
  de las Provincias Unidas y los partidos que lo integran) se presentan juntas con el nombre
  oficial, para no contar cuatro partidos donde la DINE informa uno.
- Hay 43 circuitos sin polígono en la cartografía: no se dibujan en el mapa, pero suman en
  departamento y provincia.
- En el mapa de una elección el color identifica la familia política del partido (`docs/CRITERIOS_COLOR.md`), no su puesto.
- Para seguir un circuito en el tiempo se usa el enlace histórico de la cartografía, con el
  circuito de 2023 como referencia.
- Votantes = votos positivos + blancos + nulos (+ impugnados, recurridos y comando en 2023).
  En 2003 a 2019 la base no trae impugnados, así que la participación puede quedar apenas
  por debajo de la oficial.

## Epígrafes de tablas y gráficos

Cada tabla y cada gráfico del tablero lleva debajo un epígrafe con el texto «Elaboración
propia en base a los datos obtenidos en…» y las fuentes que corresponden. Las fuentes se
definen en un solo lugar, `scripts/plantillas/epigrafes.js`, que se inyecta con
`scripts/agregar_pestanas.py`.

| Clave | Fuente que se nombra |
|---|---|
| `polar` | PoliticaArgentina/data_warehouse (escrutinios provisorios por mesa de 2003 a 2019, originados en el Atlas Electoral de Andy Tow) |
| `dine23` | Dirección Nacional Electoral (archivos por mesa y nomenclador de ámbitos de 2023, del portal de datos abiertos) |
| `cart` | Cartografía de circuitos electorales de Franco Galeano (CC BY 4.0) |
| `dinex` | Dirección Nacional Electoral (Excel de resultados por distrito, escrutinio definitivo) |
| `csv` | Base de datos electorales de Santa Fe 2011-2023 aportada por el equipo |

| Tabla o gráfico | Fuentes |
|---|---|
| Resultados comparados (Datos y objetivos) | `polar`, `dine23` |
| Mapa de la serie por circuito y ficha histórica de un circuito | `polar`, `dine23`, `cart` |
| Mapas por departamento y por circuito, seis presidencias en paralelo | `polar`, `dine23`, `cart` |
| Tabla por elección y sus indicadores | `polar`, `dine23` |
| Composición por departamento | `polar`, `dine23` |
| Corpus en cifras, evolución de las fuerzas, volatilidad, desafección, tamaño del lugar, dispersión | `polar`, `dine23` |
| Elecciones: mapa | `polar`, `dine23`, `cart` |
| Elecciones: tabla de resultados y participación | `polar`, `dine23`, `dinex`, `csv` |
| Partidos: evolución y tabla de nombres | `polar`, `dine23`, `dinex`, `csv` (y `cart` cuando la unidad es un circuito) |
| Partidos: mapa | `polar`, `dine23`, `cart` |
| Partidos: ranking por departamento | `polar`, `dine23` |

## Corrección del mapa por departamento (2003-2019)

Las capas de circuitos de 2003 a 2019 numeran los departamentos con otro código que la
geometría departamental (001 Belgrano … 022 Vera, contra 001 La Capital … 019 San Lorenzo).
El mapa por departamento de esas elecciones pintaba cada polígono con los datos de otro
departamento: entre 4 y 11 de los 19 estaban mal según la elección (2023 no tenía el
problema). Se corrigió traduciendo el código por nombre de departamento y se verificó que
el ganador pintado en cada departamento coincide con el de la tabla de resultados en las
doce instancias.
