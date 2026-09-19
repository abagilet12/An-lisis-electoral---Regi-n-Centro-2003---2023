# De dónde sale cada dato

Los archivos por mesa de la DINE **no se descargan desde
resultados.mininterior.gob.ar**: ese sitio genera los CSV en el navegador y
no sirve ningún archivo. Están en el portal de datos abiertos, y sus URLs son
directas y estables.

## Datos abiertos (datos.gob.ar)

El catálogo se consulta por API:

```bash
curl -s "https://datos.gob.ar/api/3/action/package_search?q=Resultados+Provisionales+Elecciones+2023&rows=10"
```

De ahí salieron estas URLs, que se bajan con `curl` sin autenticación:

| Elección | URL |
|---|---|
| 2023 PASO | `https://www.argentina.gob.ar/sites/default/files/dine-resultados/2023-PROVISORIOS_PASO.zip` |
| 2023 Generales | `https://www.argentina.gob.ar/sites/default/files/2023_generales_1.zip` |
| 2023 Segunda vuelta | `https://www.argentina.gob.ar/sites/default/files/2023_segundavuelta.zip` |

Hay datasets equivalentes para 2017, 2021 y 2025. Cada ZIP trae tres CSV:
resultados por mesa, nomenclador de ámbitos y colores oficiales por
agrupación.

**Conviene buscar por catálogo antes que pelearse con el sitio de
resultados.** Fue así como se consiguió la segunda vuelta de 2023, que ni la
API ni la web de resultados entregan a nivel circuito.

## Resumen de fuentes del proyecto

| Fuente | Qué aporta | Recuento |
|---|---|---|
| datos.gob.ar (DINE) | 2023, por mesa → circuito | Provisorio |
| PoliticaArgentina/data_warehouse | 2003-2019, por mesa → circuito | Provisorio |
| API DINE | 2011-2023, por departamento | Provisorio |
| Consulta de Escrutinio por Zona (JNE) | 2023, provincial | **Definitivo** |
| Atlas Electoral de Andy Tow | 2003-2019, provincial | **Definitivo** |
| `.xlsx` Votos por Localidad | 2007-2023, 30 localidades | Provisorio |
