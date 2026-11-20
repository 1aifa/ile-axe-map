#!/usr/bin/env python3
"""Gate técnico não permissivo da v4.10 candidata do Ilê Axé Map.

Valida integridade e proveniência, NÃO certifica coordenadas de porta e
NÃO autoriza promoção para o site oficial. Saída é relatório de triagem.
"""
import csv,json,math,sys
from collections import Counter
from pathlib import Path

R=Path(__file__).resolve().parents[1]
B=R/"data/v4_9_candidata"
O=R/"data/v4_10_candidata"
SRC=B/"terreiros_nacional_v4_9_candidata.geojson"
CAND=O/"terreiros_nacional_v4_10_candidata.geojson"
CSV=O/"correcoes_geograficas_1237.csv"
REP=O/"relatorio_correcao_coordenadas.json"
GATE=O/"gate_pre_publicacao.json"

def point(feature):
 g=feature.get("geometry")
 if g is None:return None
 if g.get("type")!="Point":raise AssertionError("Geometria inesperada")
 xy=g.get("coordinates")
 assert isinstance(xy,list) and len(xy)>=2
 x,y=xy[0:2]
 assert all(isinstance(z,(float,int)) and math.isfinite(z) for z in (x,y))
 assert -75<x<-32 and -35<y<6,("fora do Brasil",xy)
 return (x,y)

def main():
 base=json.loads(SRC.read_text(encoding="utf-8"))
 doc=json.loads(CAND.read_text(encoding="utf-8"))
 report=json.loads(REP.read_text(encoding="utf-8"))
 audit=list(csv.DictReader(CSV.open(encoding="utf-8",newline="")))
 a,b=base["features"],doc["features"]
 assert len(a)==len(b)==8610
 assert len(audit)==566 and len({r["entity_id"] for r in audit})==566
 assert report["lote_critico"]==566 and report["total_geojson"]==8610
 assert doc["metadata"]["nao_publicar_sem_revisao"] is True
 assert report["versao_publica_alterada"] is False
 # IDs históricos de algumas outras fontes se repetem. Comparar TODOS os
 # 8.610 registros por posição para impedir mudanças silenciosas nesses grupos.
 criticalIDs={r["entity_id"] for r in audit}
 all_recovered={f["properties"]["entity_id"]:f for f in b if f["properties"].get("recuperacao_status")=="recuperado_fonte_cnpj"}
 assert len(all_recovered)==1237
 assert len(criticalIDs & all_recovered.keys())==566
 stats=Counter()
 for pos,(before,feature) in enumerate(zip(a,b)):
  fid=feature["properties"].get("entity_id")
  assert fid==before["properties"].get("entity_id"),("ordem ou ID alterados",pos,fid)
  p=feature["properties"]
  if fid not in criticalIDs:
   assert feature==before, ("registro fora do lote modificado",fid)
   continue
  stats["criticos_inspecionados"]+=1
  assert p.get("revisao_geografica")=="pendente_confirmacao_endereco_real_da_casa"
  assert p.get("nivel_precisao_publicacao")=="nao_confirmada"
  assert p.get("exibir_ponto_como_exato") is False
  assert p["nome"]==before["properties"]["nome"]
  assert p["cep"]==before["properties"]["cep"]
  assert p["recuperacao_status"]=="recuperado_fonte_cnpj"
  s=str(p.get("geo_status") or "")
  assert "centroide_suspeito" in s or "geocode_nao_resolvido" in s,(fid,s)
  pos=point(feature)
  previous=point(before)
  if pos is None:
   stats["criticos_sem_geometria"]+=1
  elif str(p.get("coord_origin") or "")=="brasilapi_cep_v2_osm_aproximado":
   assert "centroide_suspeito" in s
   assert p.get("geo_precisao")=="aproximacao_de_cep_sem_numero_de_porta"
   stats["criticos_cep_provisorio"]+=1
   if previous!=pos:stats["coordenadas_alteradas"]+=1
  else:
   assert pos==previous,("mudança geográfica sem proveniência",fid)
   stats["criticos_coordenadas_herdadas"]+=1
 for f in b:
  if f["properties"].get("recuperacao_status")=="recuperado_fonte_cnpj":
   assert f["properties"]["nome"].strip() not in ("","Sem nome")
   if f.get("geometry") is not None:point(f)
 assert stats["criticos_inspecionados"]==566
 assert stats["criticos_cep_provisorio"]==report["contagens"].get("coordenadas_substituidas_aproximacao_cep",0)
 assert stats["criticos_sem_geometria"]>=report["contagens"].get("pontos_inseguros_ocultados",0)
 out={
   "resultado":"INTEGRIDADE_TECNICA_OK",
   "publicacao_geo_exata_autorizada":False,
   "lote_cnpj_1237_recuperado":len(all_recovered),
   "lote_critico_566":stats["criticos_inspecionados"],
   "outros_671_inalterados":671,
   "outros_registros_da_base_inalterados":8610-566,
   "estatisticas":dict(stats),
   "ressalva":"Checks de consistência não comprovam os endereços físicos ou nomes de uso. A v4.10 permanece prévia técnica, ocultando coordenadas críticas por padrão."
 }
 GATE.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print(json.dumps(out,ensure_ascii=False))
if __name__=="__main__":main()
