#!/usr/bin/env python3
"""Auditoria da v4.9: reconstituir os 90 registros genericos sem inventar nomes."""
import csv
import json
import re
from pathlib import Path

D = Path("data")
P = D / "v4_9_candidata"
def read(path):
    return json.loads((D / path).read_text(encoding="utf-8"))
def n(x):
    return re.sub(r"\s+", " ", str(x or "")).strip()
def key(postcode, address):
    return (n(postcode), n(address))
def one(rows, condition, origin):
    found = [r for r in rows if condition(r)]
    assert len(found) == 1, f"{origin}: {len(found)} correspondencias"
    return found[0]

v3 = read("terreiros_nacional_v3.geojson")["features"]
ceao = read("ceao/terreiros_ceao_complete.json")
axe = read("mapeando_axe/processed/mapeando_axe_2010_geocoded_v2_complete.json")
geo_path = P / "terreiros_nacional_v4_9_candidata.geojson"
doc = json.loads(geo_path.read_text(encoding="utf-8"))
assert len(doc["features"]) == 8573
vceao = [f for f in v3 if f["properties"].get("fontes") == "ceao" and n(f["properties"].get("nome")).casefold() == "não informado"]
vaxe = [f for f in v3 if f["properties"].get("nome") == "Terreiro Sem Nome"]
assert (len(vceao), len(vaxe)) == (66, 24)
made, triage = [], []
for i, f in enumerate(vceao):
    p = f["properties"]
    x = one(ceao, lambda r: n(r.get("nome")).casefold() == "não informado" and key(r.get("cep"), r.get("endereco")) == key(p.get("cep"), p.get("endereco")), f"CEAO {i}")
    lat, lon = x["lat"], x["lng"]
    assert -13.4 < lat < -12.5 and -39 < lon < -38.1, f"CEAO fora Salvador {x['id']}"
    photo = D / "ceao" / "fotos" / f"{x['id']}_thumb.jpg"
    prop = {
      "entity_id": f"ceao_ufba_{x['id']}", "nome": x["nome"], "municipio": "Salvador", "uf": "BA", "bairro": x.get("bairro") or "",
      "fontes": ["ceao"], "num_fontes": 1, "fonte_label": "CEAO/UFBA", "fonte_id": str(x["id"]), "ceao_id": str(x["id"]),
      "coord_origin": "ceao_ufba_fonte_geocodificada", "geo_status": "fonte_ceao_sem_precisao_de_porta",
      "nacao": x.get("nacao"), "categoria": p.get("categoria") or "Outro", "tradicao": "Candomblé",
      "tradicoes_adicionais": [], "nacoes": [], "raiz": None, "linhas": [], "pratica": None, "cruzamento": False,
      "classificacao_origem": "fonte_ceao_nao_inferida", "nome_status": "nao_declarado_fonte", "validacao_comunitaria": "pendente",
      "ano_fundacao": x.get("ano_fundacao"), "regente": x.get("regente"),
      "foto_thumb": f"data/ceao/fotos/{x['id']}_thumb.jpg" if photo.exists() else None, "versao": "v4.9_candidata_auditoria_90"}
    made.append({"type": "Feature", "geometry": {"type": "Point", "coordinates": [lon,lat]}, "properties": prop})
    triage.append({"fonte": "CEAO", "id_fonte": x["id"], "municipio": "Salvador", "uf": "BA", "status_nome": "nao_declarado_fonte", "status_geo": "fonte_historica", "nome_recuperado": "nao"})
def norm_identity(value):
    return n(value).casefold()

def match_identical_historical_record(x):
    """Somente correspondência documental estrita, nunca por geocodificação/proximidade."""
    keys = ("address_raw", "postcode", "city", "state", "leadership",
            "religion", "nation_line_raw", "foundation_raw")
    if not all(norm_identity(x.get(k)) for k in keys):
        return None
    candidates = [
        r for r in axe
        if n(r.get("name")) not in ("", "Terreiro Sem Nome")
        and all(norm_identity(r.get(k)) == norm_identity(x.get(k)) for k in keys)
    ]
    assert len(candidates) <= 1, f"Correspondencia historica ambigua: {x['source_record_id']}"
    return candidates[0] if candidates else None

mapped = missing = recovered_90 = 0
for i,f in enumerate(vaxe):
    p=f["properties"]
    x=one(axe, lambda r: r.get("name") == "Terreiro Sem Nome" and key(r.get("postcode"),r.get("address_raw")) == key(p.get("cep"),p.get("endereco")), f"Mapeando {i}")
    same_record = match_identical_historical_record(x)
    if same_record:
        recovered_90 += 1
    g=x.get("geocoding") or {}
    ok=(g.get("publication_status") == "geocoded" and isinstance(g.get("longitude"),(int,float))
        and isinstance(g.get("latitude"),(int,float)) and isinstance(g.get("confidence"),(int,float))
        and g["confidence"] >= 0.75)
    if ok: mapped+=1
    else: missing+=1
    geom={"type":"Point","coordinates":[g["longitude"],g["latitude"]]} if ok else None
    prop={
     "entity_id": f"mapeando_axe_2010_{x['source_record_id']}", "nome": same_record["name"] if same_record else x["name"], "municipio": x["city"], "uf": x["state"],
     "fontes": ["mapeando_axe_csv"], "num_fontes": 1, "fonte_label": "Mapeando Axé (CSV)", "fonte_id": str(x["source_record_id"]),
     "coord_origin": "mapeando_axe_v2_geocodificacao" if ok else "nao_geolocalizado",
     "geo_status": f"mapeando_axe_v2_{g.get('precision','rua')}_aproximado" if ok else "geocode_nao_resolvido_mapeando_axe",
     "nacao": x.get("nation_line_raw"), "categoria": "Terreiro", "tradicao": x.get("religion") or "Não especificada",
     "tradicoes_adicionais": [], "nacoes": [], "raiz": None, "linhas": [], "pratica": None, "cruzamento": False,
     "classificacao_origem": "campo_declarado_mapeando_axe",
     "nome_status": "recuperado_por_registro_historico_idêntico_pendente_validacao" if same_record else "nao_declarado_fonte",
     "nome_original": x["name"], "nome_fonte_correspondencia_id": str(same_record["source_record_id"]) if same_record else None,
     "duplicidade_documental_a_revisar": bool(same_record),
     "recuperacao_metodo": "endereco_cep_cidade_uf_lideranca_religiao_nacao_fundacao" if same_record else None,
     "validacao_comunitaria": "pendente", "geocoding_confidence": g.get("confidence") if ok else None,
     "precisao_geocodificacao": g.get("precision") if ok else None, "versao":"v4.9_candidata_auditoria_90"}
    made.append({"type":"Feature","geometry":geom,"properties":prop})
    triage.append({"fonte":"Mapeando Axe","id_fonte":x["source_record_id"],"municipio":x["city"],"uf":x["state"],"status_nome":"recuperado_mesma_fonte_mesma_identidade_documental" if same_record else "nao_declarado_fonte","status_geo":g.get("precision") if ok else "pendente","nome_recuperado":"sim_documental" if same_record else "nao"})
def generic(f):
    p=f["properties"]
    return (p.get("fontes")==["ceao"] and n(p.get("nome")).casefold()=="não informado") or (p.get("fontes")==["mapeando_axe_csv"] and p.get("nome")=="Terreiro Sem Nome")
old=[f for f in doc["features"] if not generic(f)]
assert len(doc["features"])-len(old)==53
cnpj=div=unidentified=0
for f in old:
    p=f["properties"]
    if p.get("recuperacao_status")=="recuperado_fonte_cnpj":
        cnpj+=1
        p["nome_status"]="nome_cadastral_cnpj_pendente_validacao_da_casa"
        st=str(p.get("geo_status") or "")
        if p.get("uf_divergente_fonte") and "uf_divergente" not in st: st+="|uf_divergente_fonte"
        if p.get("coordenada_divergente_fonte"):
            div+=1
            st+="|geocode_divergente_fonte_cnpj"
        p["geo_status"]=st
    if p.get("nome")=="Sem nome" and "mapeando_axe_csv" in p.get("fontes",[]):
        unidentified+=1
        p["nome_status"]="nome_da_casa_ausente_fonte"
        p["validacao_comunitaria"]="pendente"
        p["geo_status"]="geocode_nao_resolvido_diferenca_cotijuba_outeiro"
        f["geometry"]=None
assert (cnpj,div,unidentified,mapped,missing,recovered_90)==(1237,97,1,16,8,1)
assert len(made)==90 and len({f["properties"]["entity_id"] for f in made})==90
assert not ({f["properties"]["entity_id"] for f in made}&{f["properties"].get("entity_id") for f in old})
doc["features"]=old+made
assert len(doc["features"])==8610
doc["metadata"].update({
    "versao":"v4.9_candidata_auditoria_90","data_auditoria":"2026-11-19",
    "ceao_reconstituidos":66,"mapeando_reconstituidos":24,
    "nomes_genericos_sem_nome_oficial":90-recovered_90,
    "nomes_genericos_recuperados_registro_historico":recovered_90,
    "nomes_genericos_total_original":90,"ceao_coordenadas_fonte":66,
    "mapeando_geocodificado_v2":mapped,"mapeando_sem_geo_confiavel":missing,
    "outro_registro_sem_nome_e_geo":1,
    "cnpj_nomes_documentais_a_validar":cnpj,"cnpj_coordenadas_divergentes_ocultadas":div,
    "nao_publicar_sem_revisao":True})
geo_path.write_text(json.dumps(doc,ensure_ascii=False,separators=(",",":")),encoding="utf-8")
with (P/"triagem_90_genericos.csv").open("w",encoding="utf-8",newline="") as file:
    writer=csv.DictWriter(file,fieldnames=list(triage[0]))
    writer.writeheader()
    writer.writerows(triage)
print(f"AUDITORIA_OK registros={len(doc['features'])} CEAO=66 Mapeando_geocodificados={mapped} sem_geo={missing} nomes_genericos_sem_fonte={90-recovered_90} recuperados_pela_fonte={recovered_90} CNPJ={cnpj} geografia_suspeita={div}")
