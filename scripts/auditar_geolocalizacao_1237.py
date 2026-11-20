#!/usr/bin/env python3
"""Auditoria geográfica reproduzível dos 1.237 nomes CNPJ recuperados na v4.9.

NÃO substitui coordenadas e NÃO publica o mapa. Reconstrói o vínculo de cada
ocorrência CNPJ com a linha original da fonte por alinhamento bidirecional.
Gera fila de verificação individual e relatório agregado.
"""
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = DATA / "v4_9_candidata"
V3 = DATA / "terreiros_nacional_v3.geojson"
V49 = OUT / "terreiros_nacional_v4_9_candidata.geojson"
CNPJ = DATA / "cnpj" / "geocoding" / "terreiros_cnpj_geocoded.csv"
DEST = OUT / "auditoria_publicacao_1237.csv"
REPORT = OUT / "relatorio_auditoria_geografica_1237.json"

# Tipos de POI que definitivamente não demonstram o endereço de um terreiro.
POI_NAO_CONFIAVEL = {
    "musical_instrument", "seafood", "artwork", "hotel", "restaurant",
    "electronics", "gift", "pub", "bank", "supermarket", "hairdresser",
    "fuel", "post_office", "mall", "guest_house", "bus_station",
    "stadium", "company", "sport", "farm", "wood", "farmland",
}
# Mesmo um resultado "house" não comprova que a casa religiosa funciona ali.
PRECISAO_NAO_EXATA = {
    "postcode", "postal_code", "administrative", "suburb", "neighbourhood",
    "quarter", "city_block", "town", "village", "hamlet",
}

def rows(path):
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))

def digits(value):
    return "".join(c for c in str(value or "") if c.isdigit())

def normal(value):
    return " ".join(str(value or "").casefold().split())

def coords_from_source(source):
    if not source.get("lat") or not source.get("lng"):
        return None
    try:
        lon, lat = float(source["lng"]), float(source["lat"])
    except (ValueError, TypeError):
        return None
    if not (-75 < lon < -30 and -35 < lat < 6):
        return None
    return (lon, lat)

def coords_from_map(feature):
    geo = feature.get("geometry") or {}
    xy = geo.get("coordinates") or []
    return (float(xy[0]), float(xy[1])) if len(xy) >= 2 else None

def match_coords(a, b):
    return (a is not None and b is not None
            and abs(a[0]-b[0]) < 1e-5 and abs(a[1]-b[1]) < 1e-5)

def main():
    v3 = json.loads(V3.read_text(encoding="utf-8"))["features"]
    candidate = json.loads(V49.read_text(encoding="utf-8"))
    source = rows(CNPJ)
    assert len(v3) == 7755 and len(source) == 2673
    assert len(candidate["features"]) == 8610, "versão candidata diferente da esperada"
    block = v3[1271:3713]
    assert len(block) == 2442
    assert all(f["properties"].get("fonte_label") == "CNPJ" for f in block)
    assert candidate.get("metadata", {}).get("nao_publicar_sem_revisao") is True

    # A subsequência já utilizada na recuperação dos nomes permite
    # associar CNPJ+endereço sem adivinhação por proximidade geográfica.
    forward = []
    j = 0
    for f in block:
        target = digits(f["properties"].get("cep"))
        while j < len(source) and digits(source[j]["cep"]) != target:
            j += 1
        assert j < len(source), f"CEP não encontrado: {target}"
        forward.append(j)
        j += 1
    backward = [None] * len(block)
    j = len(source) - 1
    for i in range(len(block)-1, -1, -1):
        target = digits(block[i]["properties"].get("cep"))
        while j >= 0 and digits(source[j]["cep"]) != target:
            j -= 1
        assert j >= 0, f"CEP não encontrado na busca reversa: {target}"
        backward[i] = j
        j -= 1
    assert sum(a == b for a,b in zip(forward, backward)) == 2440

    recovered = {
        int(f["properties"]["indice_v3"]): f
        for f in candidate["features"]
        if f["properties"].get("recuperacao_status") == "recuperado_fonte_cnpj"
    }
    assert len(recovered) == 1237
    assert len({f["properties"]["entity_id"] for f in recovered.values()}) == 1237

    matches = {}
    for idx, f in recovered.items():
        assert 1271 <= idx < 3713, idx
        i = idx - 1271
        assert forward[i] == backward[i], f"Associação ambígua na v3: {idx}"
        src_index = forward[i]
        s = source[src_index]
        p = f["properties"]
        assert digits(p.get("cep")) == digits(s["cep"]), idx
        assert normal(p["nome"]) in {normal(s.get("razao_social")),
                                    normal(s.get("nome_fantasia"))}, (
            idx, p["nome"], s.get("razao_social"))
        matches[idx] = (f, src_index, s)

    # Repetição entre CEPs distintos é indício de geocodificação genérica,
    # não motivo para inventar uma nova coordenada.
    ceps_by_xy = defaultdict(set)
    count_by_xy = Counter()
    for idx, (_, _, s) in matches.items():
        xy = coords_from_source(s)
        if xy is not None:
            ceps_by_xy[xy].add(digits(s["cep"]))
            count_by_xy[xy] += 1

    out = []
    for idx, (f, src_index, s) in sorted(matches.items()):
        p = f["properties"]
        xy_source = coords_from_source(s)
        xy_map = coords_from_map(f)
        precision = (s.get("precision") or "").strip()
        flags = []
        if xy_source is None:
            flags.append("SEM_COORDENADA_NA_FONTE")
        if xy_map is None:
            flags.append("SEM_COORDENADA_NO_MAPA")
        if xy_source is not None and xy_map is not None and not match_coords(xy_map, xy_source):
            flags.append("MAPA_DIVERGE_DA_FONTE")
        if p.get("uf") != s.get("uf"):
            flags.append("UF_DIVERGE_DA_FONTE")
        if precision in POI_NAO_CONFIAVEL:
            flags.append("GEOCODIFICACAO_EM_POI_NAO_CONFIAVEL")
        if precision in PRECISAO_NAO_EXATA:
            flags.append("GEOCODIFICACAO_APROXIMADA")
        if xy_source is not None and len(ceps_by_xy[xy_source]) > 1:
            flags.append("MESMO_PONTO_PARA_CEPS_DISTINTOS")
        if not precision:
            flags.append("PRECISAO_DESCONHECIDA")

        # Nenhum resultado de geocodificador, isoladamente, prova endereço
        # efetivo ou nome de uso da casa. Validação comunitária está pendente.
        prioridade = ("CRITICA" if any(x in flags for x in (
            "SEM_COORDENADA_NA_FONTE", "SEM_COORDENADA_NO_MAPA",
            "MAPA_DIVERGE_DA_FONTE", "UF_DIVERGE_DA_FONTE",
            "GEOCODIFICACAO_EM_POI_NAO_CONFIAVEL",
            "MESMO_PONTO_PARA_CEPS_DISTINTOS")) else "REVISAR")
        out.append({
            "indice_v3": idx,
            "entity_id": p["entity_id"],
            "cnpj": s["cnpj"],
            "nome_documental": p["nome"],
            "nome_status": p.get("nome_status", "nome_cadastral_cnpj"),
            "cep": digits(s["cep"]),
            "logradouro_cnpj": s.get("logradouro", ""),
            "numero_cnpj": s.get("numero", ""),
            "bairro_cnpj": s.get("bairro", ""),
            "uf_fonte_cnpj": s.get("uf", ""),
            "uf_atual_mapa": p.get("uf", ""),
            "municipio_atual_mapa": p.get("municipio", ""),
            "longitude_atual_mapa": xy_map[0] if xy_map else "",
            "latitude_atual_mapa": xy_map[1] if xy_map else "",
            "longitude_fonte": xy_source[0] if xy_source else "",
            "latitude_fonte": xy_source[1] if xy_source else "",
            "precisao_fonte": precision,
            "ceps_distintos_no_ponto_fonte": len(ceps_by_xy[xy_source]) if xy_source else 0,
            "registros_no_ponto_fonte": count_by_xy[xy_source] if xy_source else 0,
            "indice_linha_cnpj_zero_based": src_index,
            "prioridade": prioridade,
            "alertas": "|".join(flags),
            "status_publicacao": "BLOQUEADO_ATE_VALIDACAO_DOCUMENTAL_E_GEOGRAFICA",
            "fonte": "data/cnpj/geocoding/terreiros_cnpj_geocoded.csv",
            "evidencia_de_correcao": "",
            "coordenada_validada_em": "",
            "revisor": "",
        })
    assert len(out) == 1237
    with DEST.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(out[0]))
        writer.writeheader()
        writer.writerows(out)
    alerts = Counter(flag for r in out for flag in r["alertas"].split("|") if flag)
    precisions = Counter(r["precisao_fonte"] or "ausente" for r in out)
    clusters = [
        {"longitude": xy[0], "latitude": xy[1], "registros": qty,
         "ceps_distintos": len(ceps_by_xy[xy])}
        for xy, qty in count_by_xy.most_common(20)
    ]
    report = {
        "dataset": "Ilê Axé Map v4.9 candidata, lote CNPJ recuperado",
        "data": "2026-11-19",
        "registros_auditados": len(out),
        "nomes_documentais_atribuidos": 1237,
        "status_nomes_religiosos_de_uso": "pendentes de validação da casa",
        "coordenadas_exatas_comprovadas_em_campo": 0,
        "observacao": "0 significa nenhuma validação de campo comprovada por esta auditoria; não significa que todas as localizações estejam erradas",
        "alertas_nao_exclusivos": dict(sorted(alerts.items())),
        "geocodificacao_precisao_na_fonte": dict(sorted(precisions.items())),
        "registros_prioridade_critica": sum(r["prioridade"] == "CRITICA" for r in out),
        "registros_prioridade_revisar": sum(r["prioridade"] == "REVISAR" for r in out),
        "maiores_clusters_fonte": clusters,
        "geojson_original_alterado": False,
        "apto_publicar_todos": False,
        "nao_publicar_sem_revisao": True,
        "metodo": "alinhamento bidirecional por subsequencia CEP nos 2442 CNPJs v3; 1237 correspondencias univocas; alertas detectados na fonte e no mapa",
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(f"AUDITORIA OK {len(out)} CNPJ. CRITICOS={report['registros_prioridade_critica']}, REVISAR={report['registros_prioridade_revisar']}. Publicacao bloqueada.")
    print("ALERTAS:", json.dumps(report["alertas_nao_exclusivos"], ensure_ascii=False))

if __name__ == "__main__":
    main()
