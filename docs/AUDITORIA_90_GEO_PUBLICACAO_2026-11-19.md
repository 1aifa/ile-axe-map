# Ilê Axé Map — fechamento da auditoria de nomes e geolocalização (19/11/2026)

## Escopo e resultado reproduzível
- Fonte de trabalho: `1aifa/ile-axe-map`, branch `correcao-nomes-auditoria-2026-11-19`.
- Recuperação CNPJ: **1.237/1.237 nomes documentais** (1.016 + 43 + 178); **0 CNPJ sem nome**.
- Reconstituição de **537 ocorrências** indevidamente incorporadas aos grupos anteriores.
- GeoJSON de revisão: **8.610 registros**, incluindo **90 ocorrências genéricas individualizadas**; não são 90 nomes nominais recuperados.
- **66 CEAO/UFBA**: fonte original mantém `Não informado`; coordenadas provenientes do acervo histórico, sem precisão de entrada comprovada.
- **24 Mapeando Axé**: fonte original mantém `Terreiro Sem Nome`; **16** com geocodificação aproximada de confiança indicada pela fonte, **8** sem correspondência geográfica confiável e sem geometria.
- Há mais **1 registro Mapeando Axé id 130**, em Belém (PA), com nome da casa ausente da fonte e divergência Cotijuba/Outeiro; sua geometria foi removida preventivamente.
- Portanto, **9 registros sem geometria segura (8 + 1)**; **90 nomes genéricos ainda exigem identificação com prova primária/comunitária**.
- **105 divergências de UF** e **97 coordenadas discordantes da fonte** no conjunto CNPJ; esses pontos foram marcados para ocultação no filtro padrão de localizações aproximadas.

## Cuidados de integridade
1. `nome` CNPJ recuperado representa **nome documental**, não confirmação de nome religioso/de uso.
2. Não substituir o nome ausente por liderança, nome de orixá, bairro ou nome fabricado. Não atribuir endereço/latitude de rua sem ligação inequívoca com a casa.
3. Manter `nome_status`, `geo_status`, `coord_origin`, IDs de origem e `validacao_comunitaria`. Não divulgar dados privados de liderança ou contato.
4. O mapa do **fork na branch de auditoria** já referencia o GeoJSON v4.9 e mostra ao leitor os avisos de proveniência e precisão. O **site oficial LABHDUFBA** continua sem publicação dessa atualização.
5. Preservar a versão anterior e tratar merge/publicação como etapa de curadoria separada. Snapshot do estado em 19/11: `snapshot-v49-auditoria-90-mapa-2026-11-19` (head `6006da0`).

## Rastreabilidade e validação técnica
- Evidência para os 1.238 originais: `data/v4_9_candidata/antes_depois_1238.csv`.
- Evidência dos 537 desagrupados: `data/v4_9_candidata/destino_537.csv`.
- Auditoria individual dos 90: `data/v4_9_candidata/triagem_90_genericos.csv`.
- Caso sem nome oficial: `data/v4_9_candidata/identidade_sem_nome_oficial_mapeando_axe_130.json`.
- Reconstrução: `scripts/build_v4_9_nomes.py`, `scripts/completar_nomes_v49_correspondencia.py`, `scripts/recuperar_nomes_v49_alinhamento_original.py`, `scripts/reparar_genericos_90_v49.py`.
- GitHub Actions validou **8.610**, **1.237**, **66**, **16**, **8**, **9** e unicidade dos IDs recuperados: https://github.com/1aifa/ile-axe-map/actions/runs/44644066019 .

## O que ainda impede declarar 100% concluído
- Obter, de fonte original ou comunidade, **90 nomes reais não informados** nos cadastros históricos.
- Confirmar **9 localizações** ausentes sem presumir coordenadas a partir de logradouros.
- Rever as **105 divergências de UF** e as **97 coordenadas CNPJ divergentes**, além dos agrupamentos reconstruídos.
- Validar os nomes de uso em campo antes de substituir a base pública.
