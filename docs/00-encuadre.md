# Encuadre de la investigación

Documento de referencia del proyecto. Fija qué se estudia, con qué recorte y bajo
qué criterios. Cualquier decisión del código que contradiga este documento es un
error del código.

## Proyecto

**Análisis electoral de la región centro 2003–2023**, práctica de investigación
(IHUCSO), inscripta en el proyecto CAI+D *"Actores, liderazgos y prácticas
políticas en la región Centro. La reconfiguración de un ethos socio político en
la democracia"*.

La pregunta de fondo es cómo cambió el voto en la Región Centro y qué relación
guarda ese cambio con transformaciones socio-económicas y culturales más amplias:
cómo el ethos cultural de la región se fue politizando y con qué efectos sobre el
comportamiento electoral.

Hitos que estructuran el período: el conflicto agrario de 2008 y la polarización
kirchnerismo / anti-kirchnerismo; el peso de la región en el triunfo de Cambiemos
en 2015; y la diferencia que Milei obtiene en la región en 2023, que compensa el
resultado adverso en la provincia de Buenos Aires.

## Objetivos de esta etapa

1. Confeccionar una base de datos con los resultados electorales de Santa Fe.
2. Visualizar con mapas y tablas los resultados por localidad y departamento.
3. Indagar la evolución del voto entre 2003 y 2023.
4. Analizar las particularidades de esa evolución en la región.
5. Elaborar una ponencia y/o trabajo escrito a partir de los resultados.

## Recorte acordado

- **Período**: 2003–2023.
- **Tipo de comicio**: únicamente **elecciones presidenciales**, con todas sus
  etapas (PASO, generales y ballotage donde corresponda).
- **Cobertura geográfica**: los 19 departamentos de la provincia de Santa Fe,
  desagregado por departamento y localidad.
- **Provincias**: esta etapa trabaja solo Santa Fe. Córdoba y Entre Ríos quedan
  en el horizonte del proyecto marco, no de esta entrega.

## Universo: 12 instancias de votación

| Año | PASO | General | Ballotage |
|---|---|---|---|
| 2003 | — (no existían) | 27-abr | no se realizó: Menem se retiró antes de la segunda vuelta |
| 2007 | — | 28-oct | no: la fórmula ganadora superó el 45% |
| 2011 | 14-ago | 23-oct | no |
| 2015 | 9-ago | 25-oct | 22-nov |
| 2019 | 11-ago | 27-oct | no |
| 2023 | 13-ago | 22-oct | 19-nov |

Tres advertencias metodológicas que se desprenden del universo:

1. **Las PASO existen recién desde 2011** (Ley 26.571). La serie tiene dos
   sub-series de distinta longitud: 6 generales comparables de punta a punta y
   5 PASO. La columna vertebral de cualquier comparación es la de generales.
2. **Los ballotages de 2015 y 2023 no son comparables con las generales**: son
   elecciones de dos opciones y saturan el mapa. Sirven para medir transferencia
   de votos entre primera y segunda vuelta, no para prolongar la serie.
3. **La etiqueta partidaria cambia entre elecciones**. El mismo espacio se llama
   FPV, Unidad Ciudadana, Frente de Todos o Unión por la Patria según el año;
   ídem Cambiemos / Juntos por el Cambio. Unificar eso es una decisión
   interpretativa: se documenta aparte y no se resuelve dentro de la base.

## Criterios estructurales de la base

1. **Solo votos absolutos.** Ningún porcentaje se almacena. Los denominadores
   (sobre positivos, sobre válidos, sobre votantes, sobre electores) se eligen y
   explicitan en la capa de análisis. Los archivos derivados previos usan
   "porcentaje sobre electores", que no es el denominador estándar.
2. **Clave geográfica estable.** La serie se ancla en `localidad_id`; el circuito
   es un atributo con vigencia, porque Santa Fe renumeró circuitos en 2023.
3. **Nada se descarta en silencio.** Un circuito sin localidad conocida se carga
   como `SIN_ASIGNAR` y se reporta en el informe de validación.
4. **Nombres**: clave normalizada para unir, nombre original para mostrar.
5. **Vocabulario cerrado de tipo de voto**: POSITIVO, BLANCO, NULO, RECURRIDO,
   IMPUGNADO. Las variantes de las fuentes se mapean a ese conjunto.
6. **Agrupación y fórmula conviven**: hasta 2007 las fuentes publican fórmulas
   (candidato a presidente y vice); desde 2011, agrupaciones. Ambas columnas
   existen y se completa la que la fuente permita.
7. **Trazabilidad**: cada fila declara de qué archivo fuente proviene, con su
   organismo, unidad original, carácter provisorio o definitivo y hash.

## Bibliografía de referencia del plan

- Nazareno, M. y Brusco, V. (2024). *Derecha radical y subjetividad política en
  la Argentina. Qué hay detrás del voto a Javier Milei.*
- Tagina, M. L. (2013). *Los argentinos ante las urnas. Un análisis del
  comportamiento electoral entre 1984 y 2007.*
- Tagina, M. L. (2024). *Elecciones 2023 en Argentina: la irrupción de la derecha
  radical en el poder.*
