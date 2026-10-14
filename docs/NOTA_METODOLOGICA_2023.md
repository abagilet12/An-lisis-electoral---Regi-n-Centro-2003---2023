# Nota metodológica: por qué 2023 se trabaja con resultados provisorios

**Esta decisión no es una limitación de la construcción de la base, sino una
consecuencia directa de una falla del sistema electoral argentino en materia
de publicación de datos.** Se deja constancia expresa para que no se lea como
un descuido metodológico de esta investigación.

## El hecho

Las elecciones presidenciales de 2023 se celebraron el 13 de agosto (PASO),
el 22 de octubre (generales) y el 19 de noviembre (segunda vuelta). **A la
fecha de este relevamiento —septiembre de 2026, más de tres años después—
los organismos responsables no han publicado los resultados del escrutinio
definitivo en formato desagregado.**

Lo que sí está disponible, y lo que no:

| Nivel | Escrutinio definitivo | Recuento provisorio |
|---|---|---|
| Provincial (distrito) | Sí, vía Consulta de Escrutinio por Zona de la Justicia Nacional Electoral | Sí |
| Departamento, circuito, mesa | **No publicado** | Sí, vía DINE |

Es decir: el dato desagregado —el único que permite construir mapas
electorales y analizar el comportamiento del voto a escala sub-provincial,
que es precisamente el objeto de esta investigación— **existe únicamente en
su versión provisoria**.

## La verificación

No se trata de una presunción. Se comprobó de tres maneras independientes:

1. **El archivo por mesa de la Dirección Nacional Electoral declara su propia
   condición**: la columna `recuento_tipo` de
   `presentacionDeResultados.csv` tiene el valor `PROVISORIO` en las 266.624
   filas del archivo de la PASO 2023 de Santa Fe. La existencia misma de esa
   columna indica que el sistema contempla una variante `DEFINITIVO` que no
   se publica.

2. **La API oficial de publicación de resultados** (`resultados.mininterior
   .gob.ar/api`) solo admite `tipoRecuento=1`, es decir, Recuento
   Provisional. No expone el escrutinio definitivo en ninguna consulta.

3. **La diferencia entre ambos recuentos es material, no marginal.**
   Contrastando el total provincial de la PASO 2023 de Santa Fe —donde sí
   contamos con las dos versiones— surge:

   | Agrupación | Definitivo (JNE) | Provisorio (DINE) | Diferencia |
   |---|---:|---:|---:|
   | La Libertad Avanza | 661.659 | 646.315 | −15.344 (−2,3 %) |
   | Juntos por el Cambio | 591.233 | 579.867 | −11.366 (−1,9 %) |
   | Unión por la Patria | 394.908 | 386.865 | −8.043 (−2,0 %) |

   Más de 34.000 votos de diferencia en una sola provincia y una sola
   instancia. No es ruido: es la magnitud de lo que el recuento provisorio
   deja fuera.

## Por qué esto es un problema institucional

El Código Electoral Nacional es inequívoco: **el escrutinio definitivo es el
acto que establece el resultado válido de una elección.** El recuento
provisorio es un adelanto de carácter informativo, sin valor legal, destinado
a satisfacer la expectativa pública la noche de los comicios.

De ello se sigue que el Estado argentino publica de manera desagregada,
accesible y reutilizable el dato **que no tiene valor legal**, y reserva el
dato que sí lo tiene a un agregado provincial consultable de a una zona por
vez, en planillas que ni siquiera son consistentes entre sí: en el archivo
del balotaje de Córdoba el nombre del distrito aparece truncado como
`Distrito: C`, y los códigos de lista interna cambian de formato entre
provincias sin documentación alguna.

Esto invierte el orden de prioridades que cabría esperar de un sistema
democrático. La transparencia electoral no se agota en informar rápido la
noche de la elección: exige que el resultado **definitivo** quede disponible
de forma desagregada, verificable y en formatos abiertos, en un plazo
razonable. Tres años es un plazo que no admite justificación técnica.

El costo de esta omisión recae sobre quien investiga. Cualquier análisis del
comportamiento electoral de 2023 a escala de localidad, departamento o
circuito —sea académico, periodístico o de control ciudadano— **está forzado
a trabajar sobre datos sin valor legal, o a no hacerse.** Esa es una barrera
de entrada a la fiscalización pública de los procesos electorales, y es
responsabilidad de los organismos que deben garantizar la publicación.

## Qué se hizo en esta base

1. La serie por localidad de 2023 usa el recuento provisorio, porque no
   existe alternativa.
2. El nivel provincial usa el escrutinio definitivo de la Justicia Nacional
   Electoral, que sí está disponible.
3. **Ambos no se mezclan nunca en un mismo cálculo.** La tabla
   `datos/procesados/serie_localidad.csv` lleva las columnas `fuente` y
   `recuento_tipo` precisamente para hacer explícita esa distinción en cada
   fila y volver imposible la confusión.
4. Toda comparación entre 2023 y años anteriores debe declarar esta
   asimetría. Las diferencias del orden del 2 % son menores que las
   variaciones políticas que se analizan, pero no son despreciables y deben
   estar enunciadas.

Si en algún momento los organismos publican el escrutinio definitivo
desagregado, la base está preparada para rehacerse con él sin cambios de
esquema: basta volver a correr `scripts/agregar_mesa_a_localidad.py` sobre
el archivo nuevo. La limitación es de la fuente, no del diseño.
