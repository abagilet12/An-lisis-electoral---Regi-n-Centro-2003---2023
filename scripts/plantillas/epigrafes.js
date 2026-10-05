/* ================= EPÍGRAFES DE TABLAS Y GRÁFICOS ================= */
const EPI_F = {
  polar: "PoliticaArgentina/data_warehouse (escrutinios provisorios por mesa de 2003 a 2019, originados en el Atlas Electoral de Andy Tow)",
  dine23: "la Dirección Nacional Electoral (archivos por mesa y nomenclador de ámbitos de 2023, del portal de datos abiertos)",
  cart: "la cartografía de circuitos electorales de Franco Galeano (CC BY 4.0)",
  dinex: "la Dirección Nacional Electoral (Excel de resultados por distrito, escrutinio definitivo)",
  csv: "la base de datos electorales de Santa Fe 2011-2023 aportada por el equipo",
  enlace: "el enlace histórico entre los circuitos de cada elección, construido por el equipo a partir de la cartografía de circuitos",
  censo: "el Censo Nacional de Población, Hogares y Viviendas 2022 (INDEC, base por radio censal), cruzado con la cartografía de circuitos para asignar cada circuito a su localidad"
};
function EPI(claves){
  const t=claves.map(k=>EPI_F[k]);
  const l=t.length>1 ? t.slice(0,-1).join(", ")+" y "+t[t.length-1] : t[0];
  return "Elaboración propia a partir de los datos obtenidos de "+l+".";
}
const EPI_BASE=["polar","dine23"], EPI_MAPA=["polar","dine23","cart"], EPI_FICHA=["polar","dine23","dinex","csv"], EPI_TAMANO=["polar","dine23","cart","censo"], EPI_SWING=["polar","dine23","cart","enlace"], EPI_SWING_TAM=["polar","dine23","cart","enlace","censo"];
/* [elemento de referencia, contenedor que lo envuelve (o null), fuentes, id opcional]
   El epígrafe se coloca justo debajo del contenedor. */
const EPI_ANCLAS = [
  ["#tabla",".tablewrap",EPI_BASE],
  ["#p-mp",".mapafila",EPI_MAPA],
  ["#p-md",".mapafila",EPI_MAPA],
  ["#leg-ms",null,EPI_MAPA],
  ["#resumen-anual",null,EPI_BASE],
  ["#leg-deptos",null,EPI_BASE],
  ["#tiles",null,EPI_BASE],
  ["#leg-serie",null,EPI_BASE],
  ["#p-vol",null,EPI_BASE],
  ["#p-des",null,EPI_BASE],
  ["#p-sw",".swingfila",EPI_SWING],
  ["#sw-mosaico",null,EPI_SWING],
  ["#tabla-swing",".tablewrap",EPI_SWING],
  ["#tabla-swing-tam",".tablewrap",EPI_SWING_TAM],
  ["#leg-tramos",null,EPI_TAMANO],
  ["#tabla-tramos",".tablewrap",EPI_TAMANO],
  ["#p-ele",".mapafila",EPI_MAPA],
  ["#ele-tabla",".tablewrap",EPI_FICHA],
  ["#ele-part",null,EPI_FICHA],
  ["#leg-par-serie",null,EPI_FICHA,"epi-par-serie"],
  ["#par-tabla",".tablewrap",EPI_FICHA,"epi-par-tabla"],
  ["#p-par",".mapafila",EPI_MAPA],
  ["#par-deptos",".tablewrap",EPI_BASE]
];
EPI_ANCLAS.forEach(([sel,envoltura,fuentes,id])=>{
  const e=$(sel); if(!e) return;
  const ref=envoltura ? e.closest(envoltura) : e;
  const p=document.createElement("p"); p.className="epi"; if(id) p.id=id;
  p.textContent=EPI(fuentes);
  ref.insertAdjacentElement("afterend",p);
});
