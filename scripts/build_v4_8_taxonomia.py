#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auditoria de taxonomia v4.8 — Ilê Axé Map
Produz crosswalk CSV + contagens por tradição/nação, com e sem recuperação
do campo bruto do Mapeando Axé. Não altera nada no repo.
"""
import json, re, unicodedata, collections, csv, os

REPO = '/home/hermes/projetos/ile-axe-map-mapeandoaxe'
GEO = f'{REPO}/data/v4_7/terreiros_nacional_v4_7.geojson'
RAW = f'{REPO}/data/mapeando_axe/processed/mapeando_axe_2010_geocoded_complete.json'
OUT = '/home/hermes/.hermes/cache/scratch/taxo_v48'
os.makedirs(OUT, exist_ok=True)

def norm(s):
    s = unicodedata.normalize('NFKD', str(s or '')).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'\s+', ' ', re.sub(r'[^a-z0-9 ]', ' ', s)).strip()

M = {}
def add(tokens, trad=None, nacoes=(), raiz=None, linhas=(), pratica=None, acao='mapear', nota=''):
    for t in tokens:
        M[norm(t)] = dict(trad=trad, nacoes=list(nacoes), raiz=raiz,
                          linhas=list(linhas), pratica=pratica, acao=acao, nota=nota)

# ---------- nível 2: matrizes / nações ----------
add(['angola', 'angola lokumbata', 'angolao', 'angola bantu'], 'Candomblé', ['Angola'])
add(['bantu', 'muxicongo', 'moxicongo', 'congo', 'kongo', 'mocambique'], 'Candomblé', ['Bantu'])
add(['ketu', 'keto', 'queto', 'ketu keta'], 'Candomblé', ['Ketu'])
add(['alaketo', 'alaketu'], 'Candomblé', ['Ketu'], raiz='Alaketo',
    nota='Alaketo é raiz/família dentro de Ketu, não nação')
add(['jeje', 'mina', 'mina jeje', 'vodum', 'jeje eba', 'jeje egba', 'mina vodum', 'gessa'],
    'Candomblé', ['Jeje'])
add(['jeje savalu'], 'Candomblé', ['Jeje'], raiz='Savalu')
add(['jeje mahin'], 'Candomblé', ['Jeje'], raiz='Mahin')
add(['nago', 'nago eba', 'nago egba', 'yoruba', 'ioruba'], 'Candomblé', ['Nagô'])
add(['oyo'], 'Candomblé', ['Oyó'])
add(['xamba'], 'Candomblé', ['Xambá'])
add(['cabinda', 'nago cabinda'], 'Candomblé', ['Cabinda'])
add(['ijexa', 'ojafurum'], 'Candomblé', ['Ijexá'])
add(['efon'], 'Candomblé', ['Efon'])
add(['nago tedo', 'tedo'], 'Candomblé', ['Nagô'], raiz='Tedô')
add(['omoloco'], 'Omoloko', [])
add(['caboclo'], 'Candomblé', ['Caboclo'])
add(['mina de caboclo'], 'Tambor de Mina', ['Caboclo'])
# ---------- cruzamentos declarados ----------
add(['jeje ijexa'], 'Candomblé', ['Jeje', 'Ijexá'])
add(['jeje nago', 'nago jeje'], 'Candomblé', ['Jeje', 'Nagô'])
add(['jeje nago eba'], 'Candomblé', ['Jeje', 'Nagô'], raiz='Ebá')
add(['oyo jeje', 'oya jeje'], 'Candomblé', ['Oyó', 'Jeje'])
add(['nago vodum', 'vodum nago'], 'Candomblé', ['Nagô', 'Jeje'])
add(['keto angola', 'angola keto'], 'Candomblé', ['Ketu', 'Angola'])
add(['keto jeje', 'jeje keto', 'angola jeje keto', 'jeje nago keto'], 'Candomblé', ['Ketu', 'Jeje'])
add(['keto ijexa', 'ijexa keto'], 'Candomblé', ['Ketu', 'Ijexá'])
add(['keto nago'], 'Candomblé', ['Ketu', 'Nagô'])
add(['nago ijexa'], 'Candomblé', ['Nagô', 'Ijexá'])
add(['keto caboclo'], 'Candomblé', ['Ketu', 'Caboclo'])
add(['angola caboclo'], 'Candomblé', ['Angola', 'Caboclo'])
add(['caboclo jeje'], 'Candomblé', ['Caboclo', 'Jeje'])
add(['caboclo nago'], 'Candomblé', ['Caboclo', 'Nagô'])
add(['angola umbanda'], 'Candomblé', ['Angola'], linhas=['Umbanda'])
add(['keto alaketo'], 'Candomblé', ['Ketu'], raiz='Alaketo')
add(['jeje angola'], 'Candomblé', ['Jeje', 'Angola'])
add(['angola paketan'], 'Candomblé', ['Angola'], raiz='Paketan')
add(['mina nago', 'mina jeje nago'], 'Candomblé', ['Jeje', 'Nagô'])
add(['oyo ijexa'], 'Candomblé', ['Oyó', 'Ijexá'])
add(['nago vodu', 'yoruba eba'], 'Candomblé', ['Nagô'])
add(['ketu nago'], 'Candomblé', ['Ketu', 'Nagô'])
add(['egba'], 'Candomblé', ['Nagô'], raiz='Egba')
add(['amburaxo angola', 'angola muxicongo', 'angola moxicongo'], 'Candomblé', ['Angola'])
add(['jeje mahin savalu'], 'Candomblé', ['Jeje'], raiz='Mahin/Savalu')
add(['ojafurum ijexa'], 'Candomblé', ['Ijexá'], raiz='Ojafurum')
add(['umbanda pura', 'umbanda tracada com xango', 'umbanda e exu', 'espirita umbandista', 'setes linhas de umbanda', 'linha branca pura'], 'Umbanda')
add(['jurema tracada'], 'Jurema')
add(['embanda'], 'Umbanda', acao='revisar')
add(['ketotapa', 'keto tapa'], 'Candomblé', ['Ketu'], raiz='Tapa', acao='revisar')
add(['grono keto', 'keto giro'], 'Candomblé', ['Ketu'], acao='revisar',
    nota='valor não reconhecido; provável erro de digitação na fonte')
# ---------- outras tradições ----------
add(['umbanda', 'unbandaime'], 'Umbanda')
add(['umbanda linha branca', 'umbanda pura linha branca', 'linha branca'],
    'Umbanda', linhas=['Linha Branca'])
add(['umbanda cruzada', 'linha cruzada'], 'Umbanda', linhas=['Linha Cruzada'])
add(['quimbanda'], 'Umbanda', linhas=['Quimbanda'])
add(['umbanda com nago', 'umbanda nativa', 'umbanda moxicongo', 'umbanda lunda kioko',
     'afro umbandista', 'umbandomble'], 'Umbanda', acao='revisar')
add(['sete linhas', 'linha de oxossi', 'linha cigana oriental', 'linha do oriente',
     'povo do oriente', 'cigano'], 'Umbanda', linhas=['Linha Branca'])
add(['jurema', 'jurema sagrada'], 'Jurema')
add(['catimbo'], 'Jurema', nota='Catimbó tratado como variante de Jurema')
add(['jare'], 'Jarê')
add(['tambor de mina', 'tore'], 'Tambor de Mina')
add(['tereco', 'tambor da mata'], 'Terecô')
add(['batuque'], 'Batuque')
add(['xango'], 'Xangô')
add(['pena e maraca', 'encantado', 'encantado pajelanca', 'pajelanca'], 'Encantaria')
add(['mesa branca'], 'Mesa Branca')
add(['espirita', 'espirita linha branca', 'espiritismo', 'kardecista', 'esoterista'],
    'Espiritismo')
add(['matriz africana', 'nacao africana', 'africana', 'africanista', 'afro',
     'afro brasileiro', 'afro brasileira'], 'Matriz Africana')
add(['candomble'], 'Candomblé')
# ---------- práticas (não são nação) ----------
add(['culto a baba egun', 'culta a baba egun', 'baba egun'], 'Candomblé', pratica='Babá Egun')
add(['tradicao de ifa', 'tradicao de ifa com candomble'], 'Candomblé', pratica='Ifá')
# ---------- ruído / administrativo ----------
add(['outro', 'outros', 'outra', 'nao informado', 'nacao', 'todas', 'mista'],
    None, acao='descartar')
add(['centro espirita'], None, acao='mapear',
    nota='rótulo institucional/nome da casa, não declaração de tradição — vai para "Não especificada"')
add(['terreiro'], None, acao='mapear',
    nota='"Terreiro" é tipo de entidade, não tradição — vai para "Não especificada"')
add(['bobo quexa', 'mucurumi', 'guine', 'angola e alma', 'gessa'], None, acao='revisar',
    nota='valor isolado não identificado; revisão humana')

MISSING = collections.Counter()

def convert_token(tok):
    n = norm(tok)
    if n in M:
        return M[n]
    MISSING[n] += 1
    return dict(trad=None, nacoes=[], raiz=None, linhas=[], pratica=None,
                acao='revisar', nota='valor sem correspondência')

def tokens_of(decl):
    """Quebra um valor declarado em pedaços mapeáveis."""
    out = []
    for part in re.split(r'\s*[,;/]\s*|\s+-\s+', str(decl or '')):
        p = norm(part)
        if not p: continue
        if p in M:
            out.append(part); continue
        # tenta " e " só se os dois lados existirem
        if ' e ' in p:
            a, b = p.split(' e ', 1)
            if a in M and b in M:
                out += [a, b]; continue
        out.append(part)
    return out

def parse(decls):
    trad, nac, raiz, lin, pra = [], [], None, [], None
    revisar = []
    for decl in decls:
        if not decl: continue
        for tok in tokens_of(decl):
            d = convert_token(tok)
            if d['acao'] == 'revisar': revisar.append(tok)
            if d['trad'] and d['trad'] not in trad: trad.append(d['trad'])
            for x in d['nacoes']:
                if x not in nac: nac.append(x)
            for x in d['linhas']:
                if x not in lin: lin.append(x)
            raiz = raiz or d['raiz']
            pra = pra or d['pratica']
    # tradição principal: a primeira que não for "Matriz Africana"
    principal = next((t for t in trad if t != 'Matriz Africana'), None) or (trad[0] if trad else None)
    adicionais = [t for t in trad if t != principal]
    return dict(tradicao=principal or 'Não especificada',
                tradicoes_adicionais=adicionais,
                nacoes=nac, raiz=raiz, linhas=lin, pratica=pra,
                cruzamento=len(set(trad)) > 1, revisar=revisar)


# ============================================================
# BUILD v4.8 — injeta a taxonomia de três níveis na base publicada
# Lê a v4.7 (que já contém toda a validação e a camada editorial),
# acrescenta tradicao / nacoes[] / raiz / linhas / pratica e grava
# candidata LADO A LADO em data/v4_8/. Não toca na v4.7.
# ============================================================
import hashlib
from datetime import datetime, timezone

GEO_IN = f'{REPO}/data/v4_7/terreiros_nacional_v4_7.geojson'
OUT = f'{REPO}/data/v4_8'
os.makedirs(OUT, exist_ok=True)

geo = json.load(open(GEO_IN))
F = geo['features']
raw = json.load(open(RAW))

idx = collections.defaultdict(list)
for r in raw:
    idx[(norm(r.get('name')), (r.get('state') or '').strip().upper())].append(r)

PRIVADAS = {'endereco', 'cep', 'telefone', 'email', 'lideranca', 'cnpj', 'place_id',
            'formatted_address', 'razao_social'}
RE_PRIVADO = re.compile(r'(\d{5}-\d{3}|\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}|'
                        r'[\w.+-]+@[\w-]+\.[\w.]+|\(\d{2}\)\s?\d{4,5}-?\d{4})')

cont_trad = collections.Counter()
cont_nac = collections.Counter()
cont_acao = collections.Counter()
revisar = collections.Counter()
recuperados = 0
sem_declaracao = 0

for f in F:
    p = f['properties']
    cat = str(p.get('categoria') or '').strip()
    nac_v47 = str(p.get('nacao') or '').strip()
    d47 = parse([nac_v47, cat])

    origem = 'campo_declarado_v47'
    d = d47
    if not d47['nacoes'] and not d47['pratica'] and not nac_v47:
        # tenta recompor a partir da fonte primária do próprio registro
        cands = []
        if 'mapeando_axe_csv' in (p.get('fontes') or []):
            cands = idx.get((norm(p.get('nome')), (p.get('uf') or '').strip().upper())) or []
        if cands:
            r0 = cands[0]
            nl = (r0.get('nation_line_raw') or '').strip()
            rel = (r0.get('religion') or '').strip()
            if nl or rel:
                d2 = parse([nl, rel])
                if d2['nacoes'] or d2['pratica'] or d2['tradicao'] != 'Não especificada':
                    d = d2
                    origem = 'fonte_bruta_recomposta'
                    recuperados += 1
    if d['tradicao'] == 'Não especificada' and not d['nacoes']:
        sem_declaracao += 1

    for t in d['revisar']:
        revisar[t] += 1
    cont_acao[origem] += 1
    cont_trad[d['tradicao']] += 1
    for n in (d['nacoes'] or ['(sem nação)']):
        cont_nac[n] += 1

    p['tradicao'] = d['tradicao']
    p['tradicoes_adicionais'] = d['tradicoes_adicionais']
    p['nacoes'] = d['nacoes']
    p['raiz'] = d['raiz']
    p['linhas'] = d['linhas']
    p['pratica'] = d['pratica']
    p['cruzamento'] = d['cruzamento']
    p['classificacao_origem'] = origem

# ---------- gates de publicação ----------
falhas = []
if len(F) != 8036:
    falhas.append(f'contagem inesperada: {len(F)}')

CHAVES_BASE = set(F[0]['properties']) - {'tradicao','tradicoes_adicionais','nacoes','raiz','linhas','pratica','cruzamento','classificacao_origem'}
for f in F:
    p = f['properties']
    extras = set(p) - CHAVES_BASE
    ruins = extras & PRIVADAS
    if ruins:
        falhas.append(f'{p.get("entity_id")}: chave privada nova {ruins}')
        break
    for k in ('tradicao', 'raiz', 'pratica'):
        v = p.get(k)
        if v and RE_PRIVADO.search(str(v)):
            falhas.append(f'{p.get("entity_id")}: valor privado em {k}')
            break
    lon, lat = f['geometry']['coordinates']
    if not (-74 <= lon <= -32 and -34 <= lat <= 6):
        falhas.append(f'{p.get("entity_id")}: coordenada fora do Brasil')
        break

meta = geo.get('metadata', {})
meta.update({
    'versao': 'v4.8',
    'taxonomia': 'tradicao (nível 1) / nacoes (nível 2, multivalorado) / raiz (nível 3)',
    'taxonomia_campos': ['tradicao', 'tradicoes_adicionais', 'nacoes', 'raiz', 'linhas',
                         'pratica', 'cruzamento', 'classificacao_origem'],
    'gerado_em': datetime.now(timezone.utc).isoformat(timespec='seconds'),
    'base_origem': 'v4.7',
})
geo['metadata'] = meta

saida = f'{OUT}/terreiros_nacional_v4_8.geojson'
tmp = saida + '.tmp'
with open(tmp, 'w', encoding='utf-8') as fh:
    json.dump(geo, fh, ensure_ascii=False, separators=(',', ':'))
os.replace(tmp, saida)

auditoria = dict(
    total=len(F),
    tradicao=dict(cont_trad),
    nacao=dict(cont_nac),
    classificacao_origem=dict(cont_acao),
    recuperados_fonte_bruta=recuperados,
    sem_declaracao=sem_declaracao,
    cruzamento=sum(1 for f in F if f['properties']['cruzamento']),
    com_nacao=sum(1 for f in F if f['properties']['nacoes']),
    valores_para_revisao=dict(revisar),
    gates_falhas=falhas,
    sha256=hashlib.sha256(open(saida, 'rb').read()).hexdigest(),
)
with open(f'{OUT}/auditoria_taxonomia_v4_8.json', 'w', encoding='utf-8') as fh:
    json.dump(auditoria, fh, ensure_ascii=False, indent=1)

print(f'gerado: {saida}')
print(f'tamanho: {os.path.getsize(saida)/1e6:.2f} MB')
print(f'total: {len(F)}  recuperados: {recuperados}  com nação: {auditoria["com_nacao"]}  cruzamento: {auditoria["cruzamento"]}')
print('tradicao:', dict(cont_trad))
print('nação:', dict(cont_nac))
print('gates:', falhas or 'OK')
