# Análisis electoral nacional en la provincia de Santa Fe 2003 - 2023

**Análisis electoral de la categoría presidente en la provincia de Santa Fe entre 2003 y 2023.**

La presente práctica de investigación se propone analizar y describir las características del voto en las provincias de Santa Fe, Córdoba y Entre Ríos. Al explorar las relaciones entre la evaluación del voto y los cambios socio-económicos y culturales más amplios.

El proceso de transición y consolidación democrática en Argentina supuso un sistema político integrado con un alto grado de nacionalización. Sin embargo, se observa que no todos los actores político-partidarios sostienen una estructura multinivel en las provincias. En términos electorales, la región centro equivale aproximadamente a un cuarto del padrón electoral nacional. A través del análisis comparado, nuestro objetivo es analizar la performance electoral para la categoría electiva presidente en la región centro (Córdoba, Santa Fe y Entre Ríos) entre 2003 y 2023.

El período se corresponde con la totalidad de elecciones presidenciales en el s. XXI. Lo cual cobra relevancia en el estudio social y político de la democracia argentina. Asimismo, la competencia electoral a escala nacional atravesó fuertes procesos de reconfiguración en torno a su oferta electoral, excepto por un actor político-partidario: el kirchnerismo.

Además, presentamos líneas de interpretación para abordar la división «rural-urbana». La cual requiere especial atención al lugar geográfico, que funciona como identidad social, trasciende las características socioeconómicas individuales y moldea las orientaciones políticas (en Auerbach et al., 2024).

Esta presentación se encuadra en una investigación más amplia, donde se analiza la politización de un ethos cultural en la región centro. En esta línea, se plantea que las ofertas electorales (generalmente opositoras al kirchnerismo) politizan o activan las identidades culturales que moviliza una definición política-partidaria al momento de los sufragios nacionales.

## Este repositorio

Base de datos y análisis de los resultados de **elecciones presidenciales en la
provincia de Santa Fe entre 2003 y 2023**, desagregados por departamento y
localidad. Práctica de investigación del IHUCSO, dentro del proyecto CAI+D
*"Actores, liderazgos y prácticas políticas en la región Centro"*.

El encuadre completo — período, universo de comicios y criterios metodológicos —
está en [`docs/00-encuadre.md`](docs/00-encuadre.md). Leerlo antes de tocar nada.

## Cómo se construye la base

```bash
pip install openpyxl
python3 src/build_db.py     # data/raw/ -> data/processed/ (CSV + SQLite)
python3 src/validate.py     # controles de integridad -> docs/informe-validacion.md

for t in tests/test_*.py; do python3 "$t"; done
```

`src/build_db.py` se ejecuta siempre desde cero: no hay estado acumulado entre
corridas. Las fuentes originales van en `data/raw/` y **no se versionan**; están
inventariadas en [`docs/02-manifiesto-fuentes.md`](docs/02-manifiesto-fuentes.md).

## Estructura

```
data/raw/         fuentes originales (fuera de Git)
data/processed/   CSV maestro + santafe_electoral.db
data/geo/         capas para los mapas
src/comunes.py    normalización y vocabularios cerrados
src/esquema.sql   esquema de la base
src/ingest/       un módulo por familia de fuente
docs/             encuadre, diccionario, manifiesto, pendientes
```

## Estado

La base se construye y se valida. Hoy tiene cargada la **capa de control**: los
totales provinciales que publica la DINE para 8 de las 12 instancias, con padrón,
participación y voto por agrupación en Santa Fe. Las 16 hojas leídas cuadran.

Falta la **serie desagregada por localidad**, que es el objetivo central: las
fuentes que la alimentan todavía no están en el repositorio. Ver
[`docs/03-pendientes.md`](docs/03-pendientes.md).

## Dos advertencias de lectura

- La base guarda **solo votos absolutos**. Los porcentajes se calculan al
  analizar, explicitando el denominador.
- La columna `espacio_politico` está vacía a propósito: agrupar FPV con Unión por
  la Patria, o Cambiemos con Juntos por el Cambio, es una decisión interpretativa
  del trabajo, no un dato de la fuente.
