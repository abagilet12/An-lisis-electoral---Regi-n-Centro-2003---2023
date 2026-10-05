/* ================= PESTAÑAS «ELECCIONES» Y «PARTIDOS» ================= */
/* Resultados por etiqueta oficial, sin agrupar en familias. Nivel base: circuito;
   departamento y provincia se obtienen sumando circuitos. */
const FN = s => s.normalize("NFD").replace(/[̀-ͯ]/g,"").toLowerCase().trim();
const FDEPS = R.dep;
const FGEO_DEP = {};
const FND = s => FN(s).replace(/^9 de julio$/,"nueve de julio");   // el mapa lo llama «9 de Julio»
M.dep.forEach(g=>{ FGEO_DEP[g.d] = FDEPS.findIndex(n=>FND(n)===FND(g.n)); });
const FEL = {}; D.elecciones.forEach(e=>FEL[e.clave]=e);
const fPct = (n,t) => t ? (100*n/t).toFixed(1).replace(".",",")+" %" : "—";
const fCol = i => i<8 ? `var(--s${i+1})` : "var(--s9)";
const FNOM = ["Blancos","Nulos","Impugnados","Recurridos","Comando"];
const fEl = c => etiquetaEl(FEL[c]);
const fAnio = c => +c.slice(0,4);

const FE = {clave:"2023-GENERAL", nivel:"dep", u:{t:"prov"}};
const FP = {key:"frente para la victoria", modo:"pct", clave:null, nivel:"dep", u:{t:"prov"}};
let FINIT = false;

/* partido (clave estable de la etiqueta) -> apariciones */
const FKEYS = {};
R.el.forEach(cl=>R.pt[cl].forEach((p,i)=>{ (FKEYS[p.k]||(FKEYS[p.k]=[])).push({clave:cl,i,p}); }));
const fNombre = k => FKEYS[k][FKEYS[k].length-1].p.n;
const fAparicion = (k,cl) => (FKEYS[k]||[]).find(a=>a.clave===cl);

/* ---------- agregación ---------- */
const FAGG = {};
function fSumar(clave, filtro){
  const n=R.pt[clave].length, v=new Array(n).fill(0), no=[0,0,0,0,0]; let el=0;
  for(const [c,plano] of Object.entries(R.ci[clave])){
    if(!filtro(c)) continue;
    for(let i=0;i<plano.length;i+=2) v[plano[i]]+=plano[i+1];
    const o=R.no[clave][c]; if(o) for(let j=0;j<5;j++) no[j]+=o[j];
    el+=R.pa[clave][c]||0;
  }
  return {v,no,el};
}
function fUnidad(clave, u){
  if(u.t==="cir" && !R.ci[clave][u.c]) return null;
  const key=clave+"|"+(u.t==="prov"?"p":u.t==="dep"?"d"+u.i:"c"+u.c);
  if(FAGG[key]) return FAGG[key];
  let a;
  if(u.t==="prov"){
    a=fSumar(clave,()=>true);
    R.pt[clave].forEach((p,i)=>{ if(p.sd) a.v[i]=p.v; });     // solo total provincial
  } else if(u.t==="dep") a=fSumar(clave,c=>R.de[clave][c]===u.i);
  else {
    const n=R.pt[clave].length, v=new Array(n).fill(0), plano=R.ci[clave][u.c];
    for(let i=0;i<plano.length;i+=2) v[plano[i]]+=plano[i+1];
    a={v,no:R.no[clave][u.c]||[0,0,0,0,0],el:R.pa[clave][u.c]||0};
  }
  a.pos=a.v.reduce((x,y)=>x+y,0);
  a.vot=a.pos+a.no.reduce((x,y)=>x+y,0);
  return FAGG[key]=a;
}
function fUnidades(clave, nivel){
  const out={};
  if(nivel==="dep") FDEPS.forEach((n,i)=>out[i]=fUnidad(clave,{t:"dep",i}));
  else for(const c of Object.keys(R.ci[clave])) out[c]=fUnidad(clave,{t:"cir",c});
  return out;
}
function fNombreU(u, clave){
  if(u.t==="prov") return "Provincia de Santa Fe";
  if(u.t==="dep") return "Departamento "+FDEPS[u.i];
  const di=R.de[clave]&&R.de[clave][u.c];
  return "Circuito "+u.c+(di!=null?" · "+FDEPS[di]:"");
}
const fGanador = a => a.v.reduce((m,x,i)=>x>a.v[m]?i:m,0);
const fPuesto = (a,i) => 1+a.v.filter(x=>x>a.v[i]).length;

/* circuito de 2023 (referencia) <-> código de otra elección */
function fCodigoEn(c23, clave){
  const e=M.eq[c23]; const cod=e&&e[clave.slice(0,4)];
  return cod && R.ci[clave][cod] ? cod : null;
}
function fAC23(cod, clave){ return refDe(cod, fAnio(clave)); }

/* ---------- selectores de unidad ---------- */
function fOpcionesU(sel, u, clave){
  let h=`<option value="p">Provincia de Santa Fe</option>`+
    FDEPS.map((n,i)=>`<option value="d${i}">Departamento ${n}</option>`).join("");
  if(u.t==="cir") h+=`<option value="c">${fNombreU(u,clave)}</option>`;
  $(sel).innerHTML=h;
  $(sel).value = u.t==="prov" ? "p" : u.t==="dep" ? "d"+u.i : "c";
}
const fLeerU = (v, actual) => v==="p" ? {t:"prov"} : v[0]==="d" ? {t:"dep",i:+v.slice(1)} : actual;

/* ---------- mapa genérico ---------- */
function fMapa(o){
  const svg=$(o.svg), H=620, L=lienzo(H), S=H/GH, esDep=o.nivel==="dep";
  svg.setAttribute("viewBox",`0 0 ${L.w} ${H}`);
  const geo = esDep ? M.dep : M.cap[CAPA(fAnio(o.clave))];
  let h="";
  for(const g of geo){
    const k = esDep ? FGEO_DEP[g.d] : g.c, a=o.datos[k];
    const sel = o.sel!=null && String(o.sel)===String(k);
    h+=`<path class="pista${sel?" sel":""}" d="${ruta(g.g,S,0,0)}" fill="${a&&a.pos?o.relleno(a,k):"var(--surface-2)"}" `+
       `stroke="var(--ground)" stroke-width="${esDep?0.9:0.35}" data-k="${k}"></path>`;
  }
  svg.innerHTML=h;
  const tip=asegurarTip(o.cont);
  svg.onpointermove=ev=>{
    const p=ev.target.closest("path"); if(!p){tip.style.display="none";return}
    const k=p.dataset.k, a=o.datos[k];
    const nom = esDep ? "Departamento "+FDEPS[k] : fNombreU({t:"cir",c:k},o.clave);
    tip.innerHTML=`<div class="th">${nom}</div>`+(a&&a.pos? o.tip(a,k) : `<div class="r"><span>Sin datos</span><b>—</b></div>`);
    posicionarTip(tip,o.cont,ev);
  };
  svg.onpointerleave=()=>tip.style.display="none";
  svg.onclick=ev=>{ const p=ev.target.closest("path"); if(p) o.clic(p.dataset.k); };
}
const fFilas = (a,clave,n) => a.v.map((x,i)=>[i,x]).filter(x=>x[1]>0).sort((x,y)=>y[1]-x[1]).slice(0,n)
  .map(([i,x])=>`<div class="r"><span><span class="sw" style="display:inline-block;background:${fCol(i)}"></span> `+
    `${R.pt[clave][i].n}</span><b>${fPct(x,a.pos)}</b></div>`).join("");

/* ================= ELECCIONES ================= */
function fCabEle(){
  const cl=FE.clave, e=FEL[cl], pt=R.pt[cl], a=fUnidad(cl,{t:"prov"});
  const g=pt[0], s=pt[1];
  $("#ele-cab").innerHTML=
    `<span><b>${fEl(cl)}</b> · ${e.fecha}</span>`+
    `<span><b>${pt.length}</b> ${pt.length===1?"partido":"partidos"}</span>`+
    `<span>Primero: <span class="g">${g.n}</span> con ${fPct(a.v[0],a.pos)}</span>`+
    (s?`<span>Margen sobre el segundo: <b>${((100*(a.v[0]-a.v[1]))/a.pos).toFixed(1).replace(".",",")} p.p.</b></span>`:"");
}
function dibujarEleccion(){
  const cl=FE.clave;
  fCabEle();
  const datos=fUnidades(cl,FE.nivel);
  const ganan=new Set();
  fMapa({svg:"#svg-ele", cont:"#p-ele", clave:cl, nivel:FE.nivel, datos,
    sel: FE.u.t==="dep"&&FE.nivel==="dep" ? FE.u.i : FE.u.t==="cir"&&FE.nivel==="cir" ? FE.u.c : null,
    relleno:a=>{const i=fGanador(a); ganan.add(i); return fCol(i);},
    tip:a=>fFilas(a,cl,4)+`<div class="r"><span>Votos positivos</span><b>${fmt(a.pos)}</b></div>`,
    clic:k=>{ FE.u = FE.nivel==="dep" ? {t:"dep",i:+k} : {t:"cir",c:k}; dibujarEleccion(); }});
  const usados=[...ganan].sort((x,y)=>x-y);
  $("#leg-ele").innerHTML=`<div class="escala"><b>Primera fuerza</b></div>`+
    usados.map(i=>`<span class="item"><i class="sw" style="background:${fCol(i)}"></i>${R.pt[cl][i].n}</span>`).join("")+
    `<div class="escala" style="margin-top:.5rem"><span style="font-size:.72rem;color:var(--ink-3)">El color indica el puesto `+
    `provincial del partido en esta elección, no su identidad.</span></div>`;
  const sinGeo = Object.keys(R.ci[cl]).filter(c=>!M.cap[CAPA(fAnio(cl))].some(g=>g.c===c));
  const vSin = sinGeo.reduce((t,c)=>t+R.ci[cl][c].filter((_,j)=>j%2).reduce((x,y)=>x+y,0),0);
  $("#ele-nota-mapa").textContent = FE.nivel==="cir"&&sinGeo.length
    ? `${sinGeo.length} circuitos sin polígono en la cartografía (${fmt(vSin)} votos) no se representan en el mapa, aunque sí se computan en el departamento y la provincia.`
    : "El recuento es provisorio; cuando existe, el total provincial definitivo de la DINE se consigna en la tabla.";
  fOpcionesU("#ele-unidad",FE.u,cl);
  fTablaEle(); fPartEle();
}
function fTablaEle(){
  const cl=FE.clave, a=fUnidad(cl,FE.u), pt=R.pt[cl], prov=FE.u.t==="prov", def=R.def[cl];
  $("#ele-tit-tabla").textContent="Resultado · "+fEl(cl);
  $("#ele-sub-tabla").textContent=fNombreU(FE.u,cl);
  if(!a){ $("#ele-tabla").innerHTML=""; $("#ele-nota-tabla").textContent="Esta unidad no existe en esta elección."; return; }
  const orden=a.v.map((x,i)=>[i,x]).filter(x=>x[1]>0||prov).sort((x,y)=>y[1]-x[1]);
  const conDef=prov && def && pt.some(p=>p.d);
  let h=`<thead><tr><th>Puesto</th><th class="nom">Partido (nombre oficial)</th><th>Votos</th><th>% positivos</th><th></th>`+
        (conDef?`<th>Definitivo DINE</th><th>% definitivo</th>`:"")+`</tr></thead><tbody>`;
  let n=0, maxp=Math.max(...orden.map(x=>x[1]/a.pos),0.0001);
  for(const [i,x] of orden){
    n++;
    const p=pt[i];
    h+=`<tr><td>${n}</td><td class="nom"><button type="button" data-k="${p.k}">${p.n}</button>`+
       `${p.sd&&!prov?" (sin detalle territorial)":""}</td><td>${fmt(x)}</td><td>${fPct(x,a.pos)}</td>`+
       `<td style="text-align:left"><span class="fbar" style="width:${Math.max(1,Math.round(150*(x/a.pos)/maxp))}px"></span></td>`+
       (conDef?`<td>${p.d?fmt(p.d):"—"}</td><td>${p.d&&def.positivos?fPct(p.d,def.positivos):"—"}</td>`:"")+`</tr>`;
  }
  h+=`</tbody><tfoot><tr><td></td><td class="nom">Votos positivos</td><td>${fmt(a.pos)}</td><td>100 %</td><td></td>`+
     (conDef?`<td>${def.positivos?fmt(def.positivos):"—"}</td><td></td>`:"")+`</tr></tfoot>`;
  $("#ele-tabla").innerHTML=h;
  $("#ele-tabla").querySelectorAll("button[data-k]").forEach(b=>b.onclick=()=>fIrPartido(b.dataset.k, cl));
  const sd=pt.filter(p=>p.sd);
  $("#ele-nota-tabla").textContent =
    (sd.length ? `${sd.map(p=>p.n).join(", ")}: solo se dispone del total provincial, sin desagregación por departamento ni circuito. `:"")+
    "El porcentaje se calcula sobre los votos positivos. Se trata del recuento provisorio; la columna definitiva proviene de la DINE.";
}
function fPartEle(){
  const cl=FE.clave, a=fUnidad(cl,FE.u), prov=FE.u.t==="prov", def=R.def[cl];
  $("#ele-sub-part").textContent=fNombreU(FE.u,cl);
  if(!a){ $("#ele-part").innerHTML=""; return; }
  const otros=a.no[2]+a.no[3]+a.no[4];
  const tiles=[["Electores",fmt(a.el)],["Votantes",fmt(a.vot)],["Participación",fPct(a.vot,a.el)],
    ["Blancos",`${fmt(a.no[0])} · ${fPct(a.no[0],a.vot)}`],["Nulos",`${fmt(a.no[1])} · ${fPct(a.no[1],a.vot)}`]];
  if(otros) tiles.push(["Impugnados, recurridos y comando",`${fmt(otros)} · ${fPct(otros,a.vot)}`]);
  $("#ele-part").innerHTML=tiles.map(([l,n])=>`<div><span class="l">${l}</span><span class="n">${n}</span></div>`).join("");
  let nota="Votantes = votos positivos + blancos + nulos"+(otros?" + impugnados, recurridos y comando":"")+
    ". El porcentaje de blancos y nulos se calcula sobre el total de votantes.";
  if(prov && def && def.electores){
    const v=def.votantes||((def.positivos||0)+(def.blancos||0)+(def.nulos||0));
    nota+=` Definitivo (DINE): ${fmt(def.electores)} electores, participación ${fPct(v,def.electores)}, `+
      `${fmt(def.blancos||0)} blancos y ${fmt(def.nulos||0)} nulos.`;
  }
  $("#ele-nota-part").textContent=nota;
}
function fIniciarEle(){
  $("#ele-sel").innerHTML=R.el.map(c=>`<option value="${c}"${c===FE.clave?" selected":""}>${fEl(c)} · ${FEL[c].fecha}</option>`).join("");
  $("#ele-sel").onchange=e=>{
    const ant=FE.clave, nueva=e.target.value;
    if(FE.u.t==="cir"){ const c23=fAC23(FE.u.c,ant), cod=c23&&fCodigoEn(c23,nueva); FE.u=cod?{t:"cir",c:cod}:{t:"prov"}; }
    FE.clave=nueva; dibujarEleccion();
  };
  $("#ele-unidad").onchange=e=>{ FE.u=fLeerU(e.target.value,FE.u); dibujarEleccion(); };
  segmento("#ele-nivel",null,v=>{ FE.nivel=v; dibujarEleccion(); });
}

/* ================= PARTIDOS ================= */
function fIrPartido(k, clave){
  FP.key=k;
  const ap=FKEYS[k]; FP.clave = clave && fAparicion(k,clave) ? clave : ap[ap.length-1].clave;
  mostrar("par");
  window.scrollTo({top:0,behavior:"smooth"});
}
function fIrEleccion(clave){
  FE.clave=clave; FE.u=FP.u.t==="dep"?FP.u:{t:"prov"}; $("#ele-sel").value=clave;
  mostrar("ele");
  window.scrollTo({top:0,behavior:"smooth"});
}
/* resultado del partido en una unidad, elección por elección */
function fSerie(k, u){
  return R.el.map(cl=>{
    const ap=fAparicion(k,cl);
    let uu=u;
    if(u.t==="cir"){ const cod=fCodigoEn(u.c,cl); uu=cod?{t:"cir",c:cod}:null; }
    const a=uu?fUnidad(cl,uu):null;
    if(!ap) return {cl,ap:null,a};
    if(!a) return {cl,ap,a:null};
    const v=a.v[ap.i];
    return {cl,ap,a,v,pct:a.pos?100*v/a.pos:0,puesto:fPuesto(a,ap.i),sd:!!ap.p.sd&&u.t!=="prov"};
  });
}
function fCabPar(){
  const k=FP.key, ap=FKEYS[k], s=fSerie(k,{t:"prov"}).filter(x=>x.ap&&x.a);
  const mejor=s.reduce((m,x)=>x.pct>m.pct?x:m,s[0]);
  const gan=s.filter(x=>x.puesto===1).length;
  $("#par-cab").innerHTML=
    `<span><b>${fNombre(k)}</b></span>`+
    `<span>Presente en <b>${ap.length}</b> de ${R.el.length} instancias</span>`+
    `<span>Mejor resultado provincial: <span class="g">${mejor.pct.toFixed(1).replace(".",",")} %</span> · ${fEl(mejor.cl)}</span>`+
    `<span>Primero en la provincia en <b>${gan}</b> ${gan===1?"instancia":"instancias"}</span>`;
}
function fVinculos(){
  const k=FP.key, ant=R.vi.filter(v=>v[1]===k), sig=R.vi.filter(v=>v[0]===k);
  let h="";
  const bt=(kk,f,tit)=>`<div>${tit} <button type="button" data-k="${kk}">${fNombre(kk)}</button>`+
                       `<div class="fte">Fuente del vínculo: ${f}</div></div>`;
  ant.forEach(v=>h+=bt(v[0],v[2],"← Etiqueta anterior:"));
  sig.forEach(v=>h+=bt(v[1],v[2],"Etiqueta siguiente →"));
  if(h) h+=`<div class="fte">El vínculo constituye una ayuda para navegar entre denominaciones y no implica que se trate del mismo partido.</div>`;
  $("#par-vinc").className="vinc"; $("#par-vinc").innerHTML=h;
  $("#par-vinc").querySelectorAll("button[data-k]").forEach(b=>b.onclick=()=>fIrPartido(b.dataset.k));
}
function dibujarPartido(){
  const k=FP.key;
  const ap=FKEYS[k];
  if(!FP.clave||!fAparicion(k,FP.clave)) FP.clave=ap[ap.length-1].clave;
  $("#par-sel").value=k;
  fOpcionesU("#par-unidad",FP.u,FP.clave);
  fCabPar(); fVinculos(); fGraficoPar(); fTablaPar(); fMapaPar();
  const epi=EPI(FP.u.t==="cir" ? EPI_FICHA.concat(["cart"]) : EPI_FICHA);
  ["epi-par-serie","epi-par-tabla"].forEach(id=>{ const e=document.getElementById(id); if(e) e.textContent=epi; });
}
function fGraficoPar(){
  const k=FP.key, s=fSerie(k,FP.u), pct=FP.modo==="pct";
  const svg=$("#svg-par-serie"), W=900, H=330, Mg={t:28,r:16,b:58,l:62};
  const valor=x=>pct?x.pct:x.v;
  const maxv=Math.max(...s.filter(x=>x.a&&x.ap).map(valor),0.0001);
  const top=pct? Math.max(10,Math.ceil(maxv/10)*10) : maxv*1.1;
  const sl=(W-Mg.l-Mg.r)/s.length, bw=sl*0.62, y=v=>H-Mg.b-(v/top)*(H-Mg.t-Mg.b);
  let o="";
  const paso=pct?(top<=50?10:20):0;
  const ticks=pct?Array.from({length:Math.floor(top/paso)+1},(_,i)=>i*paso):[0,.25,.5,.75,1].map(f=>Math.round(top*f/1000)*1000);
  for(const t of ticks) o+=`<line x1="${Mg.l}" x2="${W-Mg.r}" y1="${y(t)}" y2="${y(t)}" stroke="var(--line)"/>`+
    `<text x="${Mg.l-8}" y="${y(t)+4}" text-anchor="end" font-size="11" fill="var(--ink-3)" font-family="var(--font-d)">`+
    `${pct?t.toFixed(0)+" %":fmt(t)}</text>`;
  s.forEach((x,i)=>{
    const cx=Mg.l+sl*i+sl/2, e=FEL[x.cl];
    const col = e.instancia==="GENERAL" ? "var(--navy)" : e.instancia==="PASO" ? tinte("var(--navy)",.5) : "var(--accent)";
    if(x.ap && x.a && !x.sd){
      const v=valor(x), top_=y(v);
      o+=`<rect class="${x.cl===FP.clave?"sel":""}" data-cl="${x.cl}" x="${cx-bw/2}" y="${top_}" width="${bw}" height="${Math.max(1,H-Mg.b-top_)}" fill="${col}" `+
         `${x.cl===FP.clave?'stroke="var(--accent)" stroke-width="2"':""} style="cursor:pointer"></rect>`+
         `<text x="${cx}" y="${top_-6}" text-anchor="middle" font-size="10.5" font-weight="700" fill="var(--ink)" font-family="var(--font-d)">`+
         `${pct?v.toFixed(1).replace(".",",")+"":(v>=1000?(v/1000).toFixed(0)+" mil":v)}</text>`;
    } else {
      o+=`<text x="${cx}" y="${H-Mg.b-6}" text-anchor="middle" font-size="12" fill="var(--ink-3)" font-family="var(--font-d)">${x.ap&&x.sd?"s/d":"—"}</text>`;
    }
    o+=`<text x="${cx}" y="${H-Mg.b+17}" text-anchor="middle" font-size="11" fill="var(--ink-2)" font-family="var(--font-d)">${e.anio}</text>`+
       `<text x="${cx}" y="${H-Mg.b+30}" text-anchor="middle" font-size="9" fill="var(--ink-3)" font-family="var(--font-d)">${e.instancia==="PASO"?"PASO":e.instancia==="GENERAL"?"General":"Balotaje"}</text>`;
  });
  svg.innerHTML=o;
  svg.querySelectorAll("rect[data-cl]").forEach(r=>r.onclick=()=>{FP.clave=r.dataset.cl; dibujarPartido();});
  $("#leg-par-serie").innerHTML=
    `<span class="item"><i class="sw" style="background:var(--navy)"></i>General</span>`+
    `<span class="item"><i class="sw" style="background:${tinte("var(--navy)",.5)}"></i>PASO</span>`+
    `<span class="item"><i class="sw" style="background:var(--accent)"></i>Balotaje</span>`;
  $("#par-nota-serie").textContent =
    `${fNombreU(FP.u,FP.clave)}. El guion («—») indica que el partido no figura en esa instancia y no equivale a un cero; `+
    `«s/d» señala que solo se dispone del total provincial. Un clic en una barra selecciona la elección del mapa.`+
    (FP.u.t==="cir"?" En los circuitos se sigue el territorio de 2023 mediante el enlace histórico de la cartografía.":"");
}
function fTablaPar(){
  const k=FP.key, s=fSerie(k,FP.u);
  $("#par-sub-tabla").textContent=fNombreU(FP.u,FP.clave);
  let h=`<thead><tr><th>Elección</th><th class="nom">Nombre oficial en esa elección</th><th>Votos</th><th>% positivos</th><th>Puesto</th></tr></thead><tbody>`;
  for(const x of s){
    const sel = x.cl===FP.clave ? " sel" : "";
    if(!x.ap){ h+=`<tr class="ausente"><td>${fEl(x.cl)}</td><td class="nom">No figura en esta instancia</td><td>—</td><td>—</td><td>—</td></tr>`; continue; }
    if(!x.a || x.sd){ h+=`<tr class="ausente${sel}"><td>${fEl(x.cl)}</td><td class="nom">${x.ap.p.n}</td>`+
      `<td>${x.sd?"sin detalle territorial":"sin dato comparable"}</td><td>—</td><td>—</td></tr>`; continue; }
    h+=`<tr class="clic${sel}" data-cl="${x.cl}"><td>${fEl(x.cl)}</td><td class="nom">${x.ap.p.n}</td>`+
       `<td>${fmt(x.v)}</td><td>${fPct(x.v,x.a.pos)}</td><td>${x.puesto}.º de ${x.a.v.filter(n=>n>0).length}</td></tr>`;
  }
  $("#par-tabla").innerHTML=h+"</tbody>";
  $("#par-tabla").querySelectorAll("tr[data-cl]").forEach(r=>r.onclick=()=>{FP.clave=r.dataset.cl; dibujarPartido();});
  $("#par-nota-tabla").innerHTML=`Un clic en una fila selecciona esa elección en el mapa. <button type="button" id="par-ir-ele" style="font:inherit;color:var(--navy);background:none;border:0;padding:0;cursor:pointer;text-decoration:underline">Ver la ficha de ${fEl(FP.clave)} →</button>`;
  $("#par-ir-ele").onclick=()=>fIrEleccion(FP.clave);
}
function fMapaPar(){
  const k=FP.key, ap=FKEYS[k], cl=FP.clave, a0=fAparicion(k,cl);
  $("#par-el").innerHTML=ap.map(x=>`<option value="${x.clave}"${x.clave===cl?" selected":""}>${fEl(x.clave)}</option>`).join("");
  const i=a0.i, sd=!!a0.p.sd;
  const datos=sd?{}:fUnidades(cl,FP.nivel);
  let max=0;
  for(const a of Object.values(datos)) if(a&&a.pos) max=Math.max(max,100*a.v[i]/a.pos);
  fMapa({svg:"#svg-par", cont:"#p-par", clave:cl, nivel:FP.nivel, datos,
    sel: FP.u.t==="dep"&&FP.nivel==="dep" ? FP.u.i : FP.u.t==="cir"&&FP.nivel==="cir" ? fCodigoEn(FP.u.c,cl) : null,
    relleno:a=>tinte("var(--navy)", max? (100*a.v[i]/a.pos)/max : 0),
    tip:a=>`<div class="r"><span>${a0.p.n}</span><b>${fPct(a.v[i],a.pos)}</b></div>`+
           `<div class="r"><span>Votos</span><b>${fmt(a.v[i])}</b></div><div class="r"><span>Positivos</span><b>${fmt(a.pos)}</b></div>`,
    clic:kk=>{
      if(FP.nivel==="dep") FP.u={t:"dep",i:+kk};
      else { const c23=fAC23(kk,cl); if(!c23){ $("#par-nota-mapa").textContent="Este circuito carece de enlace histórico, por lo que no es posible seguirlo en el tiempo."; return; } FP.u={t:"cir",c:c23}; }
      dibujarPartido();
    }});
  $("#leg-par").innerHTML= sd ? `<div class="escala"><b>Sin detalle territorial</b></div>` :
    `<div class="escala"><b>${a0.p.n}</b>`+
    [0,.25,.5,.75,1].map(t=>`<span><i style="background:${tinte("var(--navy)",t)}"></i>${(max*t).toFixed(0)} %</span>`).join("")+`</div>`;
  $("#par-nota-mapa").textContent = sd
    ? "Para esta elección únicamente se conoce el total provincial del partido."
    : `${fEl(cl)}. El color varía de claro a oscuro según el porcentaje del partido sobre los votos positivos de cada unidad; la escala alcanza el máximo observado.`;
  fTablaDeptosPar(a0, sd);
}
function fTablaDeptosPar(a0, sd){
  const cl=FP.clave;
  if(sd){ $("#par-deptos").innerHTML=""; return; }
  const filas=FDEPS.map((n,d)=>{ const a=fUnidad(cl,{t:"dep",i:d}); return {d,n,a,v:a.v[a0.i],p:a.pos?100*a.v[a0.i]/a.pos:0,pu:fPuesto(a,a0.i)}; })
    .sort((x,y)=>y.p-x.p);
  $("#par-deptos").innerHTML=`<thead><tr><th class="nom">Departamento</th><th>Votos</th><th>% positivos</th><th>Puesto</th></tr></thead><tbody>`+
    filas.map(f=>`<tr class="clic${FP.u.t==="dep"&&FP.u.i===f.d?" sel":""}" data-d="${f.d}"><td class="nom">${f.n}</td>`+
      `<td>${fmt(f.v)}</td><td>${f.p.toFixed(1).replace(".",",")} %</td><td>${f.pu}.º</td></tr>`).join("")+"</tbody>";
  $("#par-deptos").querySelectorAll("tr[data-d]").forEach(r=>r.onclick=()=>{FP.u={t:"dep",i:+r.dataset.d}; dibujarPartido();});
}
function fIniciarPar(){
  const ks=Object.keys(FKEYS).sort((a,b)=>FN(fNombre(a).replace(/^Alianza /,"")).localeCompare(FN(fNombre(b).replace(/^Alianza /,""))));
  $("#par-sel").innerHTML=ks.map(k=>`<option value="${k}">${fNombre(k)} · ${FKEYS[k].length} ${FKEYS[k].length===1?"instancia":"instancias"}</option>`).join("");
  $("#par-sel").onchange=e=>{FP.key=e.target.value; FP.clave=null; dibujarPartido();};
  $("#par-unidad").onchange=e=>{FP.u=fLeerU(e.target.value,FP.u); dibujarPartido();};
  $("#par-el").onchange=e=>{FP.clave=e.target.value; dibujarPartido();};
  segmento("#par-modo",null,v=>{FP.modo=v; fGraficoPar();});
  segmento("#par-nivel",null,v=>{FP.nivel=v; fMapaPar();});
}

function fichasMostrar(p){
  if(!FINIT){ FINIT=true; fIniciarEle(); fIniciarPar(); }
  if(p==="ele") dibujarEleccion(); else dibujarPartido();
}
