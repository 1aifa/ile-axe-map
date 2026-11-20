#!/usr/bin/env python3
"""Avalia fontes geograficas preexistentes e API pública de CEP em 3 amostras."""
import csv, json, re, time, urllib.request, unicodedata
from pathlib import Path
from collections import Counter
from difflib import SequenceMatcher
R=Path(__file__).resolve().parents[1]; P=R/"data/v4_9_candidata"
audit={r["cnpj"]:r for r in csv.DictReader((P/"auditoria_publicacao_1237.csv").open(encoding="utf-8"))}
google=json.loads((R/"data/unified/google_places_results.json").read_text(encoding="utf-8"))
def norm(s):
 s=unicodedata.normalize("NFD",s or "")
 return " ".join("".join(c for c in s if unicodedata.category(c)!="Mn").casefold().split())
data=Counter(); examples=[]; review=[]
for g in google:
 if not g.get("id","").startswith("cnpj_"):continue
 c=g["id"][5:];a=audit.get(c)
 if not a:continue
 cl=g.get("classification","")
 data["cobertos"]+=1;data["class:"+cl]+=1
 if g.get("google_lat") is None or g.get("google_lng") is None:continue
 data["google_coordenadas"]+=1
 ad=norm(g.get("google_address") or "")
 zip8="".join(re.findall(r"\d",ad))
 cep=a["cep"]; found_cep=bool(re.search(r"(?<!\d)"+re.escape(cep[:5])+r"[- ]?"+re.escape(cep[5:])+r"(?!\d)",g.get("google_address") or ""))
 uf=bool(re.search(r"(?i)\b"+re.escape(a["uf_fonte_cnpj"])+r"\b",g.get("google_address") or ""))
 number=a.get("numero_cnpj","").strip()
 match_num=bool(number.isdigit() and re.search(r"(?<!\d)"+re.escape(number)+r"(?!\d)",g.get("google_address") or ""))
 sim=max(SequenceMatcher(None,norm(g.get("google_name")),norm(a["nome_documental"])).ratio(), SequenceMatcher(None,norm(g.get("google_name")),norm(g.get("nome"))).ratio())
 if found_cep:data["cep_coincidente"]+=1
 if found_cep and uf:data["cep_uf_coincidentes"]+=1
 if found_cep and uf and match_num:data["cep_uf_numero_coincidentes"]+=1
 if found_cep and uf and match_num and sim>=.5:
  data["evidencia_google_estrita"]+=1
  if a["prioridade"]=="CRITICA":data["evidencia_google_estrita_criticos"]+=1
  if examples.__len__()<12:examples.append({"cnpj":c,"nome":a["nome_documental"][:75],"google_nome":g.get("google_name"),"google_endereco":g.get("google_address"),"clas":cl,"similaridade":round(sim,2),"geo_original":[a["latitude_atual_mapa"],a["longitude_atual_mapa"]],"geo_google":[g["google_lat"],g["google_lng"]],"alertas":a["alertas"]})
 if a["prioridade"]=="CRITICA" and len(review)<10:review.append({"cnpj":c,"class":cl,"cep_igual":found_cep,"uf_igual":uf,"numero_igual":match_num,"similaridade":round(sim,2),"endereco_google":g.get("google_address","")[:180]})
# BrasilAPI CEP v2: valor de coordenadas é apenas aproximação do CEP, nunca prova de número de porta.
consultas=[]
for cep in ("08743550","35501079","40020030"):
 try:
  u="https://brasilapi.com.br/api/cep/v2/"+cep
  req=urllib.request.Request(u,headers={"User-Agent":"IleAxeMap-LABH-UFBA/1.0 (auditoria CEP pontual)","Accept":"application/json"})
  with urllib.request.urlopen(req,timeout=10) as r: item=json.load(r)
  consultas.append({"cep":cep,"state":item.get("state"),"city":item.get("city"),"street":item.get("street"),"location":item.get("location")})
 except Exception as e:consultas.append({"cep":cep,"erro":str(e)[:180]})
 time.sleep(0.5)
out={"contagens":dict(data),"exemplos_evidencia_estrita":examples,"amostras_criticas":review,"brasilapi":consultas}
(P/"analise_fontes_alternativas_1237.json").write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"contagens":dict(data),"brasilapi":consultas},ensure_ascii=False))
