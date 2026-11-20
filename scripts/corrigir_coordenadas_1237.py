#!/usr/bin/env python3
"""Corrige geocodificações evidentemente inválidas dos 1.237 CNPJ da v4.9.

ATENÇÃO: a coordenada obtida por CEP é APROXIMADA; não é porta do terreiro.
Só altera 566 registros críticos, em v4.10 candidata isolada.
Mantém original e rastreabilidade, oculta candidatos aproximados por padrão.
Não publica, não utiliza coordenadas licenciadas pelo Google Places.
"""
import csv, json, math, re, time, unicodedata, urllib.request, urllib.error
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data"
BASE=DATA/"v4_9_candidata"
OUT=DATA/"v4_10_candidata"
OUT.mkdir(exist_ok=True)
SRC=BASE/"terreiros_nacional_v4_9_candidata.geojson"
AUD=BASE/"auditoria_publicacao_1237.csv"
CACHE=OUT/"cache_cep_brasilapi_v2.jsonl"
GEO=OUT/"terreiros_nacional_v4_10_candidata.geojson"
CSV=OUT/"correcoes_geograficas_1237.csv"
REPORT=OUT/"relatorio_correcao_coordenadas.json"

def digits(s):return "".join(c for c in str(s or "") if c.isdigit())
def norm(s):
 s=unicodedata.normalize("NFD", str(s or ""))
 return re.sub(r"\s+", " ", "".join(c for c in s if unicodedata.category(c)!="Mn").casefold()).strip()
def compare_street(raw,api):
 a=norm(raw);b=norm(api)
 for word in ("rua ","avenida ","av ","travessa ","tv ","r ","estrada ","estr ","praca ","alameda ","rodovia ","viela "):
  if a.startswith(word):a=a[len(word):]
  if b.startswith(word):b=b[len(word):]
 a=re.sub(r"[^a-z0-9 ]", " ",a).strip()
 b=re.sub(r"[^a-z0-9 ]", " ",b).strip()
 if not a or not b:return None
 from difflib import SequenceMatcher
 sim=SequenceMatcher(None,a,b).ratio()
 return sim>=.58 or a in b or b in a
def xy_of(f):
 a=(f.get("geometry") or {}).get("coordinates") or []
 return (float(a[0]), float(a[1])) if len(a)>=2 else None
def dkm(p,q):
 if not p or not q:return None
 x1,y1=p;x2,y2=q
 a=math.radians(y2-y1);b=math.radians(x2-x1)
 z=math.sin(a/2)**2+math.cos(math.radians(y1))*math.cos(math.radians(y2))*math.sin(b/2)**2
 return 12742*math.asin(min(1,math.sqrt(max(0,z))))
def valid_xy(xy):
 return xy is not None and -74.5<xy[0]<-32 and -34.5<xy[1]<5.5
def load_cache():
 d={}
 if CACHE.exists():
  for line in CACHE.read_text(encoding="utf-8").splitlines():
   try:
    it=json.loads(line);d[it["cep"]]=it
   except (ValueError,KeyError):continue
 return d
def lookup_cep(cep):
 req=urllib.request.Request("https://brasilapi.com.br/api/cep/v2/"+cep,
 headers={"User-Agent":"IleAxeMap-Geocorrecao/1.0 (https://github.com/1aifa/ile-axe-map)",
          "Accept":"application/json"})
 try:
  with urllib.request.urlopen(req,timeout=10) as resp: d=json.load(resp)
  location=(d.get("location") or {}).get("coordinates") or {}
  xy=None
  try:xy=(float(location["longitude"]),float(location["latitude"]))
  except (ValueError,KeyError,TypeError):pass
  if not valid_xy(xy):xy=None
  return {"cep":cep,"state":d.get("state"),"city":d.get("city"),
          "street":d.get("street"),"neighborhood":d.get("neighborhood"),
          "xy":xy,"fonte":"BrasilAPI CEP v2; geolocalizacao derivada de OSM", "erro":None}
 except urllib.error.HTTPError as exc:
  return {"cep":cep,"erro":"HTTP_"+str(exc.code),"xy":None}
 except Exception as exc:
  return {"cep":cep,"erro":type(exc).__name__,"xy":None}

def main():
 doc=json.loads(SRC.read_text(encoding="utf-8"))
 features=doc["features"]
 assert len(features)==8610 and doc["metadata"]["nao_publicar_sem_revisao"] is True
 audit=list(csv.DictReader(AUD.open(encoding="utf-8",newline="")))
 assert len(audit)==1237
 targets=[r for r in audit if r["prioridade"]=="CRITICA"]
 assert len(targets)==566
 by_id={f["properties"].get("entity_id"):f for f in features}
 assert all(r["entity_id"] in by_id for r in targets)
 assert len({r["entity_id"] for r in targets})==566
 cache=load_cache()
 total_consultas=0
 erro429=False
 progress=[]
 unique_cep=list(dict.fromkeys(r["cep"] for r in targets if len(r["cep"])==8))
 for i,cep in enumerate(unique_cep,1):
  if cep in cache:continue
  if erro429:break
  item=lookup_cep(cep);cache[cep]=item
  with CACHE.open("a",encoding="utf-8") as f:f.write(json.dumps(item,ensure_ascii=False)+"\n")
  total_consultas+=1
  if item.get("erro") in ("HTTP_429","HTTP_403"):
   erro429=True
  if i%40==0:
   print(f"consultas CEP {i}/{len(unique_cep)}; HTTP erro={item.get('erro')}; ativas={total_consultas}",flush=True)
  time.sleep(.6)
 changes=[]; counts=Counter()
 for r in targets:
  f=by_id[r["entity_id"]];p=f["properties"]
  old=xy_of(f); it=cache.get(r["cep"]) or {}
  new=it.get("xy")
  apiuf=(it.get("state") or "").upper()
  expected=r["uf_fonte_cnpj"].upper()
  cep_ok=bool(apiuf and apiuf==expected)
  street_match=compare_street(r["logradouro_cnpj"],it.get("street"))
  flags=set(r["alertas"].split("|"))
  if p["nome"]!=r["nome_documental"]:raise AssertionError("Identidade divergente "+r["entity_id"])
  if p.get("cep")!=r["cep"]:raise AssertionError("CEP divergente "+r["entity_id"])
  severity=bool({"GEOCODIFICACAO_EM_POI_NAO_CONFIAVEL","MESMO_PONTO_PARA_CEPS_DISTINTOS",
  "MAPA_DIVERGE_DA_FONTE","SEM_COORDENADA_NA_FONTE"}&flags)
  previous_status=str(p.get("geo_status") or "")
  p["geo_status_anterior_v49"]=previous_status
  p["coordenadas_anteriores_v49"]=list(old) if old else None
  p["revisao_geografica"]="pendente_confirmacao_endereco_real_da_casa"
  p["fonte_checagem_cep"]="BrasilAPI CEP v2" if it.get("state") else None
  p["nivel_precisao_publicacao"]="nao_confirmada"
  p["exibir_ponto_como_exato"]=False
  updated=False;action=""
  if cep_ok and it.get("city"):
   if p.get("uf")!=apiuf:
    p["uf_anterior_correcao"]=p.get("uf")
    p["uf"]=apiuf
    counts["uf_corrigidas"]+=1
   if not p.get("municipio") or p.get("uf_anterior_correcao"):
    p["municipio_anterior_correcao"]=p.get("municipio")
    p["municipio"]=it["city"]
    counts["municipios_preenchidos_ou_corrigidos"]+=1
  if not cep_ok:
   # CEP / UF contraditórios: nenhuma fonte autoriza marcar ponto como correto.
   p["geo_status"]="geocode_nao_resolvido_conflito_uf_ou_cep"
   p["geo_alertas_nova_auditoria"]=r["alertas"]
   action="BLOQUEADO_CEP_UF_DIVERGEM"
   if severity:
    f["geometry"]=None;counts["pontos_inseguros_ocultados"]+=1
  elif valid_xy(new):
   distance=dkm(old,new)
   # Clusters genéricos, POIs de categoria alheia e divergências com o CSV:
   # o ponto por CEP é usado SOMENTE como posição regional provisória.
   # Não se afirma que seja a casa nem seu portão.
   if severity and (distance is None or distance>2.5):
    f["geometry"]={"type":"Point","coordinates":list(new)}
    p["coord_origin"]="brasilapi_cep_v2_osm_aproximado"
    p["geo_status"]="centroide_suspeito_cep_provisorio_nao_exato"
    p["geo_precisao"]="aproximacao_de_cep_sem_numero_de_porta"
    p["coordenada_cep_validada_em"]="2026-11-19"
    counts["coordenadas_substituidas_aproximacao_cep"]+=1
    action="SUBSTITUIDO_POR_PONTO_CEP_APROXIMADO_OCULTO_PADRAO"
    updated=True
   else:
    # Coordenada de rua só é plausível para o endereço cadastral,
    # não confirmação de que a casa religiosa opera ali.
    p["geo_status"]="geocode_nao_resolvido_exatidao_da_casa_pendente"
    p["geo_precisao"]="coordenada_anterior_nao_comprovada"
    counts["mantidos_sem_validacao_exata"]+=1
    action="COORDENADA_ANTIGA_MANTIDA_NAO_EXATA"
  else:
   p["geo_status"]="geocode_nao_resolvido_cep_sem_coordenada"
   if severity:
    f["geometry"]=None;counts["pontos_inseguros_ocultados"]+=1
   action="BLOQUEADO_SEM_COORDENADA_CEP"
  counts["revisados"]+=1
  changes.append({"entity_id":r["entity_id"],"indice_v3":r["indice_v3"],
   "cnpj":r["cnpj"],"nome_documental":r["nome_documental"],
   "cep":r["cep"],"uf_anterior":r["uf_atual_mapa"],
   "uf_cnpj":expected,"uf_brasilapi":apiuf,"cidade_brasilapi":it.get("city",""),
   "logradouro_cnpj":r["logradouro_cnpj"],"logradouro_brasilapi":it.get("street",""),
   "logradouro_compativel":street_match,
   "coord_antiga_lon":old[0] if old else "","coord_antiga_lat":old[1] if old else "",
   "coord_final_lon":xy_of(f)[0] if xy_of(f) else "",
   "coord_final_lat":xy_of(f)[1] if xy_of(f) else "",
   "distancia_antiga_cep_km":round(dkm(old,new),2) if valid_xy(new) and old else "",
   "tipo_coordenada_final":"aproximada_cep" if updated else ("indisponivel" if not xy_of(f) else "antiga_nao_comprovada"),
   "acao":action,"alertas_originais":r["alertas"],
   "fonte":"BrasilAPI CEP v2 (coordenadas OSM quando presentes)",
   "publicacao":"BLOQUEADO_ATE_VALIDACAO_LOCAL_EXATO"})
 assert counts["revisados"]==566
 assert len(changes)==566
 doc["metadata"].update({"versao":"v4.10_candidata_correcao_geografica","data_auditoria":"2026-11-19",
 "lote_critico_revisado":566,"correcoes_aproximadas_por_cep":counts["coordenadas_substituidas_aproximacao_cep"],
 "coordenadas_terreiros_confirmadas_exatas_neste_lote":0,
 "apto_publicar":False,"nao_publicar_sem_revisao":True,
 "observacao":"Coordenadas CEP são marcadores aproximados; ocultos no filtro padrao. Identidade da casa nao comprovada."})
 GEO.write_text(json.dumps(doc,ensure_ascii=False,separators=(",",":")),encoding="utf-8")
 with CSV.open("w",encoding="utf-8",newline="") as fh:
  w=csv.DictWriter(fh,fieldnames=list(changes[0]));w.writeheader();w.writerows(changes)
 report={"versao":"v4.10_candidata_correcao_geografica","base":"v4.9_candidata_auditoria_90",
 "total_geojson":len(features),"lote_critico":566,"total_cep_distintos_alvo":len(unique_cep),
 "consultas_cep_executadas_nesta_rodada":total_consultas,"ceps_com_cache":len(cache),
 "interrompido_por_rate_limit":erro429,"contagens":dict(counts),
 "coord_exata_confirmada":0,"versao_publica_alterada":False,
 "auditoria_arquivo":"data/v4_10_candidata/correcoes_geograficas_1237.csv",
 "status":"CANDIDATA NAO PUBLICAR", "nota":"Ponto CEP é regional/aproximado, não entrada do terreiro. 671 outros registros ainda aguardam validação. Nomes de uso não comprovados."}
 REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print("CORRECOES GEO:",json.dumps(report,ensure_ascii=False),flush=True)
if __name__=="__main__":main()
