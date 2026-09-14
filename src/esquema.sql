-- Esquema de la base electoral de Santa Fe (presidenciales 2003-2023).
-- Lo genera src/build_db.py; no se edita a mano la base, se edita este archivo.

PRAGMA foreign_keys = ON;

-- Las 12 instancias del periodo. 'cargada' dice si ya tiene datos.
CREATE TABLE dim_eleccion (
    eleccion_id        TEXT PRIMARY KEY,
    anio               INTEGER NOT NULL,
    instancia          TEXT NOT NULL CHECK (instancia IN ('PASO','GENERAL','BALLOTAGE')),
    fecha              TEXT NOT NULL,
    orden_cronologico  INTEGER NOT NULL,
    cargada            INTEGER NOT NULL DEFAULT 0,
    nota               TEXT
);

-- Los 19 departamentos, con el codigo oficial de la DINE (1..19). El codigo es
-- la clave estable para unir con las capas geograficas de los mapas.
CREATE TABLE dim_departamento (
    departamento_id   TEXT PRIMARY KEY,
    departamento      TEXT NOT NULL,
    codigo_dine       INTEGER NOT NULL UNIQUE,
    distrito_id       INTEGER NOT NULL,
    distrito          TEXT NOT NULL,
    anio_nomenclador  INTEGER NOT NULL
);

CREATE TABLE dim_localidad (
    localidad_id     TEXT PRIMARY KEY,
    localidad        TEXT NOT NULL,
    departamento_id  TEXT NOT NULL,
    departamento     TEXT NOT NULL
);

-- El circuito es un atributo con vigencia, no una clave de la serie:
-- Santa Fe renumero circuitos en 2023 y la localidad tiene que sobrevivir a eso.
CREATE TABLE dim_circuito (
    circuito_id      TEXT NOT NULL,
    eleccion_id      TEXT NOT NULL REFERENCES dim_eleccion(eleccion_id),
    departamento_id  TEXT NOT NULL,
    departamento     TEXT,
    localidad_id     TEXT NOT NULL,
    localidad        TEXT,
    fuente_id        TEXT,
    PRIMARY KEY (circuito_id, eleccion_id)
);

-- 'espacio_politico' queda vacio a proposito: agrupar FPV/UxP o Cambiemos/JxC
-- es una decision interpretativa que se define y documenta aparte.
CREATE TABLE dim_agrupacion (
    agrupacion_key    TEXT NOT NULL,
    eleccion_id       TEXT NOT NULL REFERENCES dim_eleccion(eleccion_id),
    nombre_fuente     TEXT NOT NULL,
    formula           TEXT,
    etiqueta_tipo     TEXT NOT NULL CHECK (etiqueta_tipo IN ('AGRUPACION','FORMULA')),
    espacio_politico  TEXT,
    PRIMARY KEY (agrupacion_key, eleccion_id)
);

CREATE TABLE fuentes (
    fuente_id             TEXT PRIMARY KEY,
    archivo               TEXT NOT NULL,
    eleccion_id           TEXT REFERENCES dim_eleccion(eleccion_id),
    organismo             TEXT,
    archivo_origen        TEXT,
    unidad_original       TEXT,
    recuento              TEXT,
    cobertura_declarada   TEXT,
    fecha_proceso_origen  TEXT,
    sha256                TEXT,
    observaciones         TEXT
);

-- Tabla de hechos en formato largo. Solo votos absolutos: ningun porcentaje
-- se almacena, se calculan en la capa de analisis explicitando el denominador.
CREATE TABLE hechos_votos (
    eleccion_id               TEXT NOT NULL REFERENCES dim_eleccion(eleccion_id),
    anio                      INTEGER NOT NULL,
    instancia                 TEXT NOT NULL,
    departamento_id           TEXT NOT NULL,
    departamento              TEXT,
    localidad_id              TEXT NOT NULL REFERENCES dim_localidad(localidad_id),
    localidad                 TEXT,
    tipo_voto                 TEXT NOT NULL
        CHECK (tipo_voto IN ('POSITIVO','BLANCO','NULO','RECURRIDO','IMPUGNADO')),
    agrupacion_key            TEXT,
    agrupacion_nombre_fuente  TEXT,
    formula                   TEXT,
    votos                     INTEGER NOT NULL CHECK (votos >= 0),
    fuente_id                 TEXT REFERENCES fuentes(fuente_id),
    -- Solo los votos positivos tienen agrupacion; los demas, nunca.
    CHECK ((tipo_voto = 'POSITIVO' AND agrupacion_key IS NOT NULL)
        OR (tipo_voto <> 'POSITIVO' AND agrupacion_key IS NULL))
);

CREATE TABLE padron (
    eleccion_id      TEXT NOT NULL REFERENCES dim_eleccion(eleccion_id),
    departamento_id  TEXT NOT NULL,
    localidad_id     TEXT NOT NULL REFERENCES dim_localidad(localidad_id),
    mesas            INTEGER,
    electores        INTEGER,
    fuente_id        TEXT REFERENCES fuentes(fuente_id),
    PRIMARY KEY (eleccion_id, localidad_id)
);

-- Descuadres detectados durante la ingesta. Nunca se corrigen en silencio.
CREATE TABLE incidencias (
    eleccion_id   TEXT,
    localidad_id  TEXT,
    control       TEXT,
    esperado      INTEGER,
    obtenido      INTEGER,
    diferencia    INTEGER
);

-- Totales publicados por la DINE, agregados por distrito. No son parte de la
-- serie: son el patron contra el cual se contrasta lo que arroja la base.
CREATE TABLE control_totales (
    eleccion_id     TEXT NOT NULL REFERENCES dim_eleccion(eleccion_id),
    ambito          TEXT NOT NULL CHECK (ambito IN ('PAIS','PROVINCIA')),
    distrito        TEXT NOT NULL,
    tipo_voto       TEXT NOT NULL,
    agrupacion_key  TEXT,
    nombre_fuente   TEXT,
    formula         TEXT,
    votos           INTEGER NOT NULL CHECK (votos >= 0),
    fuente_id       TEXT NOT NULL
);

CREATE TABLE control_padron (
    eleccion_id  TEXT NOT NULL REFERENCES dim_eleccion(eleccion_id),
    ambito       TEXT NOT NULL,
    distrito     TEXT NOT NULL,
    electores    INTEGER,
    mesas        INTEGER,
    votantes     INTEGER,
    fuente_id    TEXT NOT NULL
);

CREATE INDEX ix_control_eleccion ON control_totales (eleccion_id, ambito);

CREATE INDEX ix_hechos_eleccion   ON hechos_votos (eleccion_id);
CREATE INDEX ix_hechos_localidad  ON hechos_votos (localidad_id);
CREATE INDEX ix_hechos_depto      ON hechos_votos (departamento_id);
CREATE INDEX ix_hechos_agrupacion ON hechos_votos (agrupacion_key);

-- Vista de uso frecuente: totales por localidad y eleccion, con el padron al lado.
CREATE VIEW v_totales_localidad AS
SELECT h.eleccion_id,
       h.anio,
       h.instancia,
       h.departamento_id,
       h.departamento,
       h.localidad_id,
       h.localidad,
       SUM(CASE WHEN h.tipo_voto = 'POSITIVO'  THEN h.votos ELSE 0 END) AS positivos,
       SUM(CASE WHEN h.tipo_voto = 'BLANCO'    THEN h.votos ELSE 0 END) AS blancos,
       SUM(CASE WHEN h.tipo_voto = 'NULO'      THEN h.votos ELSE 0 END) AS nulos,
       SUM(CASE WHEN h.tipo_voto = 'RECURRIDO' THEN h.votos ELSE 0 END) AS recurridos,
       SUM(CASE WHEN h.tipo_voto = 'IMPUGNADO' THEN h.votos ELSE 0 END) AS impugnados,
       SUM(h.votos)                                                     AS votantes,
       p.electores,
       p.mesas
FROM hechos_votos h
LEFT JOIN padron p
       ON p.eleccion_id = h.eleccion_id AND p.localidad_id = h.localidad_id
GROUP BY h.eleccion_id, h.localidad_id;
