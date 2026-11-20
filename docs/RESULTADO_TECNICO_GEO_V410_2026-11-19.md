# Geopublicação — resultado técnico da primeira v4.10 gerada

**Origem:** artefato `ile-axe-map-v410-coordenadas-candidata` do [GitHub Actions 44656377694](https://github.com/1aifa/ile-axe-map/actions/runs/44656377694), com arquivos e validação de contagens bem-sucedidos. O job falhou **apenas no push**, por branch remota atualizada durante a execução, sem afetar o artefato ZIP já gerado. Outra execução trata o conflito com `git fetch/rebase`.

## Resultado do artefato

| Critério | Total |
|---|---:|
| Feições na candidata | 8.610 |
| Identidades CNPJ com nome documental recuperado | 1.237 |
| Críticos tratados pela rotina de geografia | 566 |
| CEPs distintos consultados | 558/558 |
| Coordenadas substituídas por ponto de CEP **aproximado** | 287 |
| UFs ajustadas conforme fonte do CEP | 103 |
| Municípios preenchidos/ajustados | 557 |
| Coordenadas antigas preservadas, sem certificação | 172 |
| Endereços com logradouro incompatível | 56 |
| Endereços sem logradouro comprovável | 41 |
| CEP e UF incompatíveis | 9 |
| Sem coordenada na fonte de CEP | 1 |
| Geometrias suspeitas removidas do mapa candidato | 79 |
| Pontos geográficos exatos confirmados nesta rotina | **0** |

As seis categorias de ação dos 566 críticos são mutuamente exclusivas e somam 566. UFs, municípios e geometrias removidas são contagens de atributos operacionais que podem se sobrepor a essas categorias.

## Cautela — clusters antigos ainda visíveis em auditoria

A inspeção independente do GeoJSON gerado detectou entre os registros críticos **121 ocorrências** com a coordenada histórica compartilhada `[-46.6391624, -23.5383214]`. Outros clusters de 23 e 10 registros críticos continuam com coordenadas coincidentes. Esses pontos são **suspeitos**: coincidência de coordenadas entre múltiplas casas não prova identidade de localização. A rotina marca todos os críticos como não homologados e a prévia os oculta por padrão.

As novas coordenadas via CEP também podem ser compartilhadas e são apenas localização regional, **não a entrada ou a porta da casa**. A edição de campo `geo_status` e o filtro na prévia não autorizam exposição como endereço exato.

## Próxima liberação

1. Concluir gravação do GeoJSON v4.10 na branch `correcao-geocoordenadas-1237-2026-11-19`.
2. Validar em CI que os 8.610 registros preservam sua identidade, os 566 críticos foram segregados, e os 671 CNPJ restantes não foram alterados.
3. Confrontar os clusters residuais, CEPs, endereços completos e a situação atual das casas com fontes independentes ou equipe de campo.
4. Só promover pontos para precisão de entrada após verificação documental, geográfica e curatorial.
5. Separar o teste de permissão de publicação da divulgação de dados: `teste-publicacao-geolocalizacao.html` usa apenas pontos v4.8 já públicos.

**Bloqueio mantido:** `nao_publicar_sem_revisao=true`. A v4.10 ainda não é um substituto homologado da base pública.
