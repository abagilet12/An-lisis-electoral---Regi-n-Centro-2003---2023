# Análisis electoral de la región centro, 2003–2023

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
python3 tests/test_derivados.py
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
