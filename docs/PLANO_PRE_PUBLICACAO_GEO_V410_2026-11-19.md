# Ilê Axé Map — preparação da publicação geográfica v4.10

**Status:** pré-publicação técnica. **Não publicar como mapa oficial** até haver validação documental e geográfica, revisão dos mantenedores e consentimento para divulgação de localizações sensíveis quando aplicável.

## Escopo e histórico

- Fork: `1aifa/ile-axe-map`, branch `correcao-geocoordenadas-1237-2026-11-19`.
- Base inicial: v4.9 candidata com 8.610 feições e 1.237 nomes CNPJ documentais recuperados.
- Registro dos 537 agrupamentos indevidos: `data/v4_9_candidata/destino_537.csv`; não reagrupar por proximidade.
- Auditoria individual: `data/v4_9_candidata/auditoria_publicacao_1237.csv` — 566 críticos, 671 em revisão.
- Fonte CNPJ: `data/cnpj/geocoding/terreiros_cnpj_geocoded.csv`, com problemas históricos de coordenadas compartilhadas e POIs de categorias alheias.
- Primeira execução da v4.10 [GitHub Actions 44652236744](https://github.com/1aifa/ile-axe-map/actions/runs/44652236744): cancelada por atingir o limite de 25 minutos após consultar 480 dos 558 CEPs distintos. **Nenhum GeoJSON de correção dessa execução foi salvo.**
- Reexecução com paralelismo controlado: [workflow de correção geográfica](https://github.com/1aifa/ile-axe-map/actions/workflows/corrigir-coordenadas-1237.yml).
- Novo GeoJSON candidato, após execução validada: `data/v4_10_candidata/terreiros_nacional_v4_10_candidata.geojson`.
- Trilha de mudanças esperada: `data/v4_10_candidata/correcoes_geograficas_1237.csv`, `relatorio_correcao_coordenadas.json`.
- Gate de integridade (somente após criação do candidato): `scripts/qa_pre_publicacao_v410.py`, com relatório `gate_pre_publicacao.json`.
- Interface de revisão isolada: `pre-publicacao-geolocalizacao.html` (não é `index.html`).

## Nível de confiança das coordenadas

1. **Endereço físico comprovado:** exigir documentação inequívoca da casa, correspondência com nome de uso, rua, número, município, UF e coordenada/entrada. Não há certificação dessa classe nesta rodada.
2. **Coordenada aproximada de CEP (v4.10):** usada exclusivamente como posição regional provisória quando CEP/UF/logradouro possuem correspondência. Campo `geo_status=centroide_suspeito_cep_provisorio_nao_exato`, `coord_origin=brasilapi_cep_v2_osm_aproximado`. **Ocultar por padrão e não divulgar como localização exata.**
3. **Coordenada antiga não comprovada:** preservar histórico, marcar revisão pendente e ocultar como precisa.
4. **Sem evidência suficiente:** geometria nula nos registros críticos de maior risco, sem inventar ponto.

Em todos os casos, separar nome cadastral de CNPJ do nome religioso ou de uso. A localização cadastrada de uma associação não prova que exista terreiro ativo naquele endereço. Não divulgar dados privados de lideranças.

## Checklist de liberação

- [ ] Execução da correção v4.10 concluída com sucesso e relatórios commitados.
- [ ] Gate `QA de integridade v4.10` concluído com sucesso.
- [ ] 8.610 feições preservadas, 1.237 identidades CNPJ rastreadas, 566 críticos isolados e 671 demais registros não alterados pela correção.
- [ ] Nenhum ponto de CEP promovido à categoria de localização exata.
- [ ] Verificação manual de amostra de cada categoria de problemas, sobretudo CEPs e UFs contraditórios.
- [ ] Validação comunitária/curatorial dos nomes e localizações cuja precisão se pretenda afirmar.
- [ ] Aceite explícito dos responsáveis pelo projeto para promover uma versão publicável.
- [ ] Conferência visual em navegador e dispositivo móvel, com busca, filtros e sem quebra de carregamento.
- [ ] Snapshot/tag do commit da produção imediatamente antes de qualquer merge.
- [ ] Plano de reversão via rollback do commit de publicação e cache do GitHub Pages.

## Publicação de teste sem afetar produção

Uma página de teste autocontida está no fork em `teste-publicacao-geolocalizacao-2026-11-19`. O compare com `LABHDUFBA/ile-axe-map:main` mostrou **somente um arquivo HTML novo**. A integração tentou criar arquivo/PR diretamente no repositório oficial, mas recebeu `403 Resource not accessible by integration`. Isso não demonstra que o usuário esteja sem permissão via interface GitHub; exige autenticação/ação manual do mantenedor.

- [Comparar e abrir PR de teste manualmente](https://github.com/LABHDUFBA/ile-axe-map/compare/main...1aifa:teste-publicacao-geolocalizacao-2026-11-19?expand=1).
- Revisar o diff e, se autorizado, enviar como PR draft ao repositório oficial.
- Não substituir `index.html` nem alterar a fonte usada pelo site durante esse teste.

## Proteções

A branch principal do projeto oficial, o `index.html` oficial e as fontes de dados de produção não são modificados por estes scripts. O rótulo `nao_publicar_sem_revisao: true` é obrigatório enquanto os registros não forem revisados. A conclusão técnica de CI não é uma homologação da geografia.
