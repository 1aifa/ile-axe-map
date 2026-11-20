#!/usr/bin/env python3
"""Sondagem de arquivos de geocodificacao previamente presentes na base."""
from pathlib import Path
import csv, json
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/"data"/"v4_9_candidata"
TARGET=[
"data/unified/google_places_results.json",
"data/cnpj/geocoding/nominatim_results.json",
"data/unified/validation_all_sources_v2.geojson",
"data/mapeando_axe/geocoding/google_places_v2_results.json",
"data/v4_2/municipios_coords.json",
]
out={}
for pth in TARGET:
 f=ROOT/pth
 try:
  with f.open(encoding="utf-8") as r: j=json.load(r)
  if isinstance(j,list):
   sample=j[:2];typ="array";length=len(j);keys=list(sample[0]) if sample and isinstance(sample[0],dict) else []
  elif isinstance(j,dict):
   typ="dict";length=len(j);keys=list(j)[:20]
   if "features" in j and isinstance(j["features"],list):
    length=len(j["features"]);sample=j["features"][:2]
   else: sample=[{"key":k,"value":v} for k,v in list(j.items())[:2]]
  else: typ=str(type(j));length=0;keys=[];sample=[]
  out[pth]={"type":typ,"length":length,"keys":keys,"sample":sample}
 except Exception as e:out[pth]={"error":str(e)}
P.joinpath("sondagem_fontes_geo.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)[:23000],encoding="utf-8")
print(json.dumps({k:{"type":v.get("type"),"length":v.get("length"),"keys":v.get("keys")} for k,v in out.items()},ensure_ascii=False))
