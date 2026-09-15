"""Descarga las fuentes electorales desde el portal de datos abiertos.

Fuente: catálogo CKAN de datos.gob.ar, datasets "Resultados Provisionales
Elecciones <año>" publicados por el Ministerio del Interior / DINE. Son archivos
a nivel mesa, pensados para descarga masiva, que alimentan src/ingest/dine_mesa.py.

Dos advertencias que quedan registradas con cada archivo:

1. **Son recuentos PROVISORIOS.** El escrutinio definitivo lo publica la Justicia
   Nacional Electoral en padron.gob.ar, cuyas condiciones de uso restringen la
   consulta a pedidos individuales: no se automatiza desde acá. Ver docs/03-pendientes.md.
2. **2003 y 2007 no están en el portal.** Son anteriores a esta política de datos
   abiertos y siguen dependiendo de otras fuentes.
"""

from __future__ import annotations

import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

import comunes as c  # noqa: E402

DESTINO = RAIZ / "data" / "raw" / "descargas"
CATALOGO = "https://datos.gob.ar/api/3/action/package_search"

#: Sin User-Agent, el portal responde 403. Se identifica el proyecto, que es lo
#: que corresponde al consultar un servicio publico de forma automatizada.
CABECERAS = {
    "User-Agent": "analisis-electoral-region-centro/1.0 (investigacion academica; IHUCSO/UNL)",
}


def _abrir(url: str, timeout: int):
    return urllib.request.urlopen(urllib.request.Request(url, headers=CABECERAS), timeout=timeout)

#: Los años con eleccion presidencial. 2013, 2017, 2021 y 2025 son legislativas
#: y quedan fuera del encuadre (ver docs/00-encuadre.md).
ANIOS_PRESIDENCIALES = {"2011", "2015", "2019", "2023"}


def catalogo() -> list[dict]:
    """Consulta el catálogo y devuelve los ZIP de años presidenciales."""
    url = (f"{CATALOGO}?q=" + urllib.parse.quote("resultados electorales OR escrutinio OR electoral")
           + "&rows=40")
    with _abrir(url, 90) as r:
        datos = json.load(r)

    salida = []
    for paquete in datos["result"]["results"]:
        titulo = paquete.get("title", "")
        if "Resultados Provisionales" not in titulo:
            continue
        anio = titulo.strip()[-4:]
        if anio not in ANIOS_PRESIDENCIALES:
            continue
        for recurso in paquete.get("resources", []):
            if (recurso.get("format") or "").upper() != "ZIP":
                continue
            salida.append({
                "anio": anio,
                "nombre": recurso.get("name", ""),
                "url": recurso.get("url", ""),
                "dataset": titulo,
            })
    return sorted(salida, key=lambda d: (d["anio"], d["nombre"]))


def descargar(recurso: dict, destino: Path) -> dict:
    """Baja un recurso. Devuelve su estado; no aborta el resto si falla."""
    archivo = destino / f"{recurso['anio']}_{c.clave(recurso['nombre'])}.zip"
    if archivo.exists():
        return {**recurso, "estado": "ya estaba", "archivo": archivo.name,
                "bytes": archivo.stat().st_size, "sha256": c.sha256_archivo(archivo)}
    try:
        with _abrir(recurso["url"], 300) as r, open(archivo, "wb") as fh:
            while bloque := r.read(1 << 20):
                fh.write(bloque)
    except Exception as err:  # una URL caída del catálogo no frena las demás
        archivo.unlink(missing_ok=True)
        return {**recurso, "estado": f"FALLO: {type(err).__name__} {err}", "archivo": None}
    return {**recurso, "estado": "descargado", "archivo": archivo.name,
            "bytes": archivo.stat().st_size, "sha256": c.sha256_archivo(archivo)}


def main() -> int:
    DESTINO.mkdir(parents=True, exist_ok=True)
    recursos = catalogo()
    print(f"{len(recursos)} recursos de años presidenciales en el catálogo\n")

    resultados = [descargar(r, DESTINO) for r in recursos]
    for res in resultados:
        if res["archivo"]:
            print(f"  {res['anio']}  {res['nombre'][:54]:54} {res['bytes']/1048576:6.1f} MB  {res['estado']}")
        else:
            print(f"  {res['anio']}  {res['nombre'][:54]:54} {res['estado'][:60]}")

    manifiesto = DESTINO / "manifiesto.json"
    manifiesto.write_text(json.dumps(resultados, indent=2, ensure_ascii=False), encoding="utf-8")
    ok = [r for r in resultados if r["archivo"]]
    print(f"\n{len(ok)} de {len(resultados)} descargados "
          f"({sum(r['bytes'] for r in ok)/1048576:.0f} MB). Manifiesto: {manifiesto.relative_to(RAIZ)}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
