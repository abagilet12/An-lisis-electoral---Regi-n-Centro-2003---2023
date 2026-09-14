"""Utilidades compartidas por todo el pipeline.

Centraliza las decisiones de normalizacion para que ninguna capa invente
criterios propios: si algo cambia aca, cambia en toda la base.
"""

from __future__ import annotations

import hashlib
import re
import unicodedata

# --- Vocabularios cerrados -------------------------------------------------

INSTANCIAS = ("PASO", "GENERAL", "BALLOTAGE")

TIPOS_VOTO = ("POSITIVO", "BLANCO", "NULO", "RECURRIDO", "IMPUGNADO")

#: Variantes con que las fuentes nombran cada tipo de voto.
_ALIAS_TIPO_VOTO = {
    "POSITIVO": "POSITIVO",
    "POSITIVOS": "POSITIVO",
    "BLANCO": "BLANCO",
    "EN BLANCO": "BLANCO",
    "VOTOS EN BLANCO": "BLANCO",
    "NULO": "NULO",
    "NULOS": "NULO",
    "RECURRIDO": "RECURRIDO",
    "RECURRIDOS": "RECURRIDO",
    "IMPUGNADO": "IMPUGNADO",
    "IMPUGNADOS": "IMPUGNADO",
    "COMANDO": "IMPUGNADO",  # 'voto de comando electoral', minoritario en DINE
}

#: Las 12 instancias presidenciales del periodo, con su fecha oficial.
CALENDARIO = {
    "2003-GENERAL": ("2003-04-27", 1, "Sin PASO. El ballotage previsto no se realizo: Menem se retiro."),
    "2007-GENERAL": ("2007-10-28", 2, "Sin PASO. Sin ballotage: la formula ganadora supero el 45%."),
    "2011-PASO": ("2011-08-14", 3, "Primeras PASO presidenciales (Ley 26.571)."),
    "2011-GENERAL": ("2011-10-23", 4, "Sin ballotage."),
    "2015-PASO": ("2015-08-09", 5, ""),
    "2015-GENERAL": ("2015-10-25", 6, ""),
    "2015-BALLOTAGE": (
        "2015-11-22", 7,
        "Primer ballotage efectivo. Solo 2 formulas: no comparable en magnitud con la general.",
    ),
    "2019-PASO": ("2019-08-11", 8, ""),
    "2019-GENERAL": ("2019-10-27", 9, "Sin ballotage."),
    "2023-PASO": ("2023-08-13", 10, ""),
    "2023-GENERAL": ("2023-10-22", 11, ""),
    "2023-BALLOTAGE": (
        "2023-11-19", 12,
        "Solo 2 formulas: no comparable en magnitud con la general.",
    ),
}

#: Que identifica la etiqueta partidaria en cada fuente. Es un hecho documentado
#: de las fuentes, no una inferencia: hasta 2007 la unidad publicada es la formula
#: (candidato a presidente y vice); desde 2011 es la agrupacion/alianza.
ETIQUETA_POR_ELECCION = {
    "2003-GENERAL": "FORMULA",
    "2007-GENERAL": "FORMULA",
    "2011-PASO": "AGRUPACION",
    "2011-GENERAL": "AGRUPACION",
    "2015-PASO": "AGRUPACION",
    "2015-GENERAL": "AGRUPACION",
    "2015-BALLOTAGE": "AGRUPACION",
    "2019-PASO": "AGRUPACION",
    "2019-GENERAL": "AGRUPACION",
    "2023-PASO": "AGRUPACION",
    "2023-GENERAL": "AGRUPACION",
    "2023-BALLOTAGE": "AGRUPACION",
}

#: Localidad a la que se imputan los circuitos sin asignacion conocida.
#: Nunca se descartan filas en silencio (criterio 3 del encuadre).
LOCALIDAD_SIN_ASIGNAR = "SIN_ASIGNAR"


# --- Normalizacion ---------------------------------------------------------

def sin_acentos(texto: str) -> str:
    """Quita tildes y dieresis conservando la enie como 'N'."""
    descompuesto = unicodedata.normalize("NFD", texto)
    return "".join(c for c in descompuesto if unicodedata.category(c) != "Mn")


def clave(texto: str | None) -> str | None:
    """Clave normalizada para unir entre fuentes y anios.

    Mayusculas, sin acentos, sin puntuacion, espacios colapsados a '_'.
    El nombre original se conserva aparte para mostrar.
    """
    if texto is None:
        return None
    t = sin_acentos(str(texto)).upper()
    t = re.sub(r"[^A-Z0-9]+", "_", t)
    return t.strip("_") or None


def normalizar_nombre(texto: str | None) -> str | None:
    """Limpia un nombre para mostrar: colapsa espacios, saca comillas sueltas."""
    if texto is None:
        return None
    return re.sub(r"\s+", " ", str(texto)).strip().strip("'\"") or None


def normalizar_tipo_voto(texto: str) -> str:
    """Lleva la etiqueta de la fuente al vocabulario cerrado de 5 valores."""
    t = sin_acentos(str(texto)).upper().strip()
    t = re.sub(r"\s+", " ", t)
    if t not in _ALIAS_TIPO_VOTO:
        raise ValueError(f"Tipo de voto desconocido: {texto!r}")
    return _ALIAS_TIPO_VOTO[t]


def a_entero(valor) -> int:
    """Convierte a entero tolerando separadores de miles y celdas vacias."""
    if valor is None or valor == "":
        return 0
    if isinstance(valor, (int,)):
        return int(valor)
    if isinstance(valor, float):
        if abs(valor - round(valor)) > 1e-9:
            raise ValueError(f"Se esperaba un entero y vino {valor!r}")
        return int(round(valor))
    t = str(valor).strip().replace(".", "").replace(",", "").replace(" ", "")
    if t in ("", "-"):
        return 0
    return int(t)


def eleccion_id(anio: int, instancia: str) -> str:
    """Identificador canonico de una instancia electoral, p. ej. '2015-BALLOTAGE'."""
    if instancia not in INSTANCIAS:
        raise ValueError(f"Instancia invalida: {instancia!r}")
    ident = f"{anio}-{instancia}"
    if ident not in CALENDARIO:
        raise ValueError(f"{ident} no es una instancia presidencial del periodo 2003-2023")
    return ident


def sha256_archivo(ruta) -> str:
    """Hash del archivo fuente, para el manifiesto de trazabilidad."""
    h = hashlib.sha256()
    with open(ruta, "rb") as fh:
        for bloque in iter(lambda: fh.read(1 << 20), b""):
            h.update(bloque)
    return h.hexdigest()
