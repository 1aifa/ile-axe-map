#!/usr/bin/env python3
"""Cria uma prévia ESTÁTICA mínima e anonimizada dos 288 pontos CEP.

Esta prévia não publica o GeoJSON bruto, nomes de casas, CPF/CNPJ,
CEPs, lideranças ou coordenadas antigas. Pin é regional, não localização.
Separa verificação técnica do projeto cultural e da homologação comunitária.
"""
import html, json, re
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"data/v4_10_candidata"
OUT=ROOT/"preview_geo_segura"
def main():
 d=json.loads((BASE/"terreiros_nacional_v4_10_candidata.geojson").read_text("utf-8"))
 gate=json.loads((BASE/"gate_pre_publicacao.json").read_text("utf-8"))
 report=json.loads((BASE/"relatorio_correcao_coordenadas.json").read_text("utf-8"))
 assert gate["resultado"]=="INTEGRIDADE_TECNICA_OK" and gate["publicacao_geo_exata_autorizada"] is False
 assert len(d["features"])==8610 and gate["lote_cnpj_1237_recuperado"]==1237
 assert report["contagens"]["coordenadas_substituidas_aproximacao_cep"]==288
 points=[]
 for f in d["features"]:
  p=f.get("properties") or {}
  if p.get("coord_origin")!="brasilapi_cep_v2_osm_aproximado":continue
  if p.get("geo_status")!="centroide_suspeito_cep_provisorio_nao_exato":continue
  c=(f.get("geometry") or {}).get("coordinates")
  assert isinstance(c,list) and len(c)>=2
  assert p.get("exibir_ponto_como_exato") is False
  uf=str(p.get("uf") or "").strip().upper()
  assert re.fullmatch("[A-Z]{2}",uf),("UF inválida",uf)
  # Geometria está apenas para visualizar dispersão do CEP.
  # Nenhuma entidade, nome, CNPJ, CEP, endereço ou líder é exposta.
  points.append({"longitude":round(float(c[0]),5),
                 "latitude":round(float(c[1]),5),"uf":uf})
 assert len(points)==288, len(points)
 # Não incluir vários marcadores no mesmo local; a contagem aparece no popup.
 grouped={}
 for a in points:
  key=(a["longitude"],a["latitude"],a["uf"])
  grouped[key]=grouped.get(key,0)+1
 safe=[{"lon":k[0],"lat":k[1],"uf":k[2],"n":v} for k,v in sorted(grouped.items())]
 htmltext="""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
 <meta name="viewport" content="width=device-width,initial-scale=1">
 <meta name="robots" content="noindex,nofollow,noarchive">
 <title>Ilê Axé Map — Prévia geográfica de teste v4.10</title>
 <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
 <style>
 *{box-sizing:border-box}body{margin:0;background:#fbf7ef;color:#261d19;font:15px/1.55 system-ui,sans-serif}
 header,main,footer{max-width:1080px;margin:auto;padding:22px}
 h1{font-size:clamp(25px,5vw,40px);line-height:1.15;margin:8px 0;color:#633b28}
 .eyebrow{font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:#99642d;font-size:11px}
 .warning{border-left:4px solid #b77d33;background:#fff0d1;border-radius:6px;padding:15px;margin:17px 0}
 .stats{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin:20px 0}
 .stat{border:1px solid #ded5c7;border-radius:9px;background:#fff;padding:14px}
 .stat b{display:block;font-size:29px;color:#804920}.stat small{color:#65594f}
 .toolbar{background:white;border:1px solid #ded5c7;padding:12px;border-radius:9px;display:flex;align-items:center;flex-wrap:wrap;gap:12px}
 #map{height:480px;background:#e7eeea;border:1px solid #dfd5c7;border-radius:10px;margin:12px 0}
 select{font:inherit;padding:9px;border-radius:7px;border:1px solid #b9aa97;background:white}
 a{color:#844a2c}.muted{color:#675d54;font-size:13px}
 @media(max-width:620px){#map{height:390px}.stats{grid-template-columns:1fr}}
 </style></head><body>
 <header><div class="eyebrow">Ilê Axé Map · Prévia experimental independente</div>
 <h1>Geolocalização: teste v4.10</h1>
 <p>Esta página demonstra os pontos regionais aproximados derivados dos CEPs no conjunto de correções. O site oficial não foi alterado.</p>
 <div class="warning"><b>Não são endereços dos terreiros.</b> Os marcadores indicam apenas uma posição geográfica aproximada de CEP, não a casa religiosa nem sua entrada. Dados de identificação e endereços foram deliberadamente retirados. Nenhum ponto foi validado em campo nesta etapa.</div></header>
 <main><div class="stats">
 <div class="stat"><b>288</b><small>Posições provisórias por CEP geradas na v4.10</small></div>
 <div class="stat"><b>78</b><small>Geometrias críticas ocultadas na candidata</small></div>
 <div class="stat"><b>0</b><small>Localizações exatas comprovadas nesta rodada</small></div></div>
 <div class="toolbar"><label for="uf">Filtrar estado:</label><select id="uf"><option value="">Todo o Brasil</option></select>
 <span id="shown" class="muted">Carregando pontos de teste...</span></div>
 <div id="map" role="region" aria-label="Mapa de pontos aproximados anônimos por CEP"></div>
 <p class="muted">Os pontos representam exclusivamente a dispersão de 288 CEPs corrigidos na candidata. Múltiplos registros podem compartilhar a mesma posição. Não substitui a validação documental, comunitária ou em campo.</p>
 <p><a href="https://github.com/1aifa/ile-axe-map/tree/correcao-geocoordenadas-1237-2026-11-19">Código e trilha da auditoria</a></p></main>
 <footer class="muted">Prévia de teste independente · Dados anonimizados · Ilê Axé Map · 2026</footer>
 <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
 <script>const DATA=__DATA__;
 (function(){
 const sel=document.getElementById('uf'),shown=document.getElementById('shown');
 const ufs=[...new Set(DATA.map(p=>p.uf))].sort();
 for(const uf of ufs){const o=document.createElement('option');o.value=uf;o.textContent=uf;sel.appendChild(o)}
 if(!window.L){shown.textContent='Não foi possível carregar a biblioteca do mapa';return}
 const map=L.map('map',{scrollWheelZoom:false}).setView([-14.2,-51.9],4);
 L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',{attribution:'&copy; OpenStreetMap contributors',maxZoom:18}).addTo(map);
 const layer=L.layerGroup().addTo(map);
 function draw(){
  layer.clearLayers();const b=[];let count=0;
  DATA.filter(p=>!sel.value||p.uf===sel.value).forEach(p=>{
    const m=L.circleMarker([p.lat,p.lon],{radius:Math.min(10,5+Math.log2(p.n)),color:'#a16b2f',weight:1,fillColor:'#cf9c55',fillOpacity:.68});
    const panel=document.createElement('div');
    panel.textContent=p.n+' registro(s) em posição aproximada de CEP · '+p.uf+' · Não é o endereço da casa.';
    m.bindPopup(panel);m.addTo(layer);b.push([p.lat,p.lon]);count+=p.n;
  });
  shown.textContent=count+' registros em '+b.length+' posições aproximadas';
  if(b.length)map.fitBounds(b,{padding:[25,25],maxZoom:10});
 }
 sel.addEventListener('change',draw);draw();
 })();</script></body></html>"""
 htmltext=htmltext.replace("__DATA__",json.dumps(safe,ensure_ascii=False,separators=(",",":")))
 assert "cnpj" not in htmltext.lower().replace("sem cnpj","") or "dados anonimizados" in htmltext
 OUT.mkdir(exist_ok=True)
 (OUT/"index.html").write_text(htmltext,encoding="utf-8")
 (OUT/".nojekyll").write_text("",encoding="utf-8")
 (OUT/"robots.txt").write_text("User-agent: *\nDisallow: /\n",encoding="utf-8")
 print(json.dumps({"arquivo":str(OUT/"index.html"),"marcadores_agrupados":len(safe),"registros":sum(x["n"] for x in safe),"ufs":len(ufs) if False else len(set(x["uf"] for x in safe))},ensure_ascii=False))
if __name__=="__main__":main()
