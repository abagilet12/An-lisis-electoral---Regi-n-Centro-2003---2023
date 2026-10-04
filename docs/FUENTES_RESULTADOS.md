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
