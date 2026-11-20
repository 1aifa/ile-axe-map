# Ilê Axé Map — fechamento da auditoria de nomes e geolocalização (19/11/2026)

## Escopo e resultado reproduzível
- Fonte de trabalho: `1aifa/ile-axe-map`, branch `correcao-nomes-auditoria-2026-11-19`.
- Recuperação CNPJ: **1.237/1.237 nomes documentais** (1.016 + 43 + 178); **0 CNPJ sem nome**.
- Reconstituição de **537 ocorrências** indevidamente incorporadas aos grupos anteriores.
- GeoJSON de revisão: **8.610 registros**, incluindo **90 ocorrências genéricas individualizadas**; não são 90 nomes nominais recuperados.
- **66 CEAO/UFBA**: fonte original mantém `Não informado`; coordenadas provenientes do acervo histórico, sem precisão de entrada comprovada.
- **24 Mapeando Axé**: **1** nome documental recuperado por ficha histórica coincidente e **23** ainda com o nome genérico da fonte; **16** com geocodificação aproximada e **8** sem geocodificação confiável.
- Há mais **1 registro Mapeando Axé id 130**, em Belém (PA), com nome da casa ausente da fonte e divergência Cotijuba/Outeiro; sua geometria foi removida preventivamente.
- Portanto, **9 registros sem geometria segura (8 + 1)**; dentre os 90 originais, **1 recuperado documentalmente e 89 ainda sem nome próprio**.
- **105 divergências de UF** e **97 coordenadas discordantes da fonte** no conjunto CNPJ; esses pontos foram marcados para ocultação no filtro padrão de localizações aproximadas.

## Correspondência documental recuperada no grupo dos 90
- Origem **Mapeando Axé 2010**, registro `176`: rótulo original `Terreiro Sem Nome`.
- Na **mesma fonte**, registro `3070` traz o nome **Centro Espírita Cabocla Jacira** (Jaboatão dos Guararapes, PE).
- Os dois registros coincidem em **endereço completo, CEP, município, UF, liderança declarada, religião, nação e ano de fundação (1971)**. Há uma pequena variação ortográfica no regente.
- O nome foi recuperado na ficha 176 como **correspondência documental pendente de validação comunitária**. O campo `duplicidade_documental_a_revisar=true` exige avaliar se as ocorrências devem ser consolidadas.
- A correspondência exata endereço+CEP foi verificada para os 66 registros CEAO selecionados, sem segunda ficha nominal que permitisse atribuição segura. As outras 23 fichas genéricas Mapeando Axé também não tiveram correspondente com o conjunto estrito de atributos.

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
- GitHub Actions confirmou **1 nome recuperado dos 90**, além de **8.610**, **1.237**, **66**, **16**, **8**, **9**: https://github.com/1aifa/ile-axe-map/actions/runs/44645993286 .

## O que ainda impede declarar 100% concluído
- Obter, de fonte original ou comunidade, **89 nomes reais não informados** nos cadastros históricos.
- Confirmar **9 localizações** ausentes sem presumir coordenadas a partir de logradouros.
- Rever as **105 divergências de UF** e as **97 coordenadas CNPJ divergentes**, além dos agrupamentos reconstruídos.
- Validar os nomes de uso em campo antes de substituir a base pública.
