# Ilê Axé Map — liberação de publicação do lote CNPJ (19/11/2026)

**Situação: NÃO LIBERADO.** Auditoria automática concluída em 1.237/1.237 registros, mas **nenhuma correção de coordenadas foi aprovada ou aplicada**. Os 1.237 nomes são nomes **documentais** do CNPJ; isso não prova nome religioso/de uso, nem que todo CNPJ represente um terreiro em atividade ou aberto à visitação.

## Resultado da verificação independente

- 1.237 registros recuperados rastreados, em ordem, à linha da fonte CSV CNPJ; sem correspondências ambíguas no lote.
- 566 registros de prioridade **CRÍTICA**, com pelo menos um alerta estrutural, de fonte ou de repetição suspeita.
- 671 registros com prioridade **REVISAR**; não são 671 coordenadas exatas já confirmadas.
- 345 geocodificações apontam para categorias de pontos de interesse não confiáveis para o endereço da casa.
- 422 compartilham coordenada da fonte com registros de CEPs diferentes.
- 300 registros aparecem num único ponto `musical_instrument` de São Paulo (296 CEPs distintos).
- 27 registros aparecem num único ponto `seafood` no Rio de Janeiro (27 CEPs distintos).
- 105 divergências de UF entre mapa e fonte CNPJ.
- 54 coordenadas do **mapa v4.9 atual** divergem da coordenada vinculada à linha original do CNPJ, segundo tolerância de 1e-5 graus; as 97 divergências do relatório anterior diziam respeito ao confronto feito na *terceira passagem com a v3*, por isso **não são contagens equivalentes**.
- 43 registros sem coordenadas na fonte original.
- 275 registros classificados em tipos explicitamente aproximados (por exemplo CEP, bairro e unidades administrativas).

**Atenção:** os alertas se sobrepõem; não devem ser somados. O campo de "prioridade" atribui a cada um dos 1.237 registros apenas uma categoria.

## Arquivos de trabalho

- `data/v4_9_candidata/auditoria_publicacao_1237.csv`: 1 linha por registro com identidade, CNPJ, endereço cadastral, UF, coordenada antiga, coordenada original, precisão, alertas e campos vazios para evidência de correção.
- `data/v4_9_candidata/relatorio_auditoria_geografica_1237.json`: totais e clusters para inspeção.
- `scripts/auditar_geolocalizacao_1237.py`: reproduz resultados localmente com `python scripts/auditar_geolocalizacao_1237.py`.
- `.github/workflows/auditoria-geografica-1237.yml`: testa cada vínculo e salva CSV/JSON. Não altera o site público.

## Protocolo de correção

1. **Identidade/nome:** confirmar a instituição representada pelo CNPJ e seu nome religioso/de uso por documento da própria comunidade, cadastro público ou fonte independente. Preservar razão social separadamente.
2. **Endereço:** para cada caso, confrontar endereço atual, CEP, número, bairro, município, UF e CNPJ com pelo menos uma fonte verificável. Não assumir que sede administrativa e casa religiosa são o mesmo endereço.
3. **Geolocalização:** descartar clusters genéricos e resultados de POI alheios ao endereço. Regeocodificar o endereço completo e conferir bairro, UF, geometria e qualidade da resposta. Só marcar como `endereco_exato` quando houver evidência de número/entrada; caso contrário, registrar `aproximado`.
4. **Conflitos:** resolver 105 UF divergentes usando evidência do endereço e do CNPJ, não somente troca automática de sigla. Conferir os 54 pontos que diferem entre mapa e fonte.
5. **Duplicidades:** manter separados os 537 registros reconstituídos, salvo prova explícita de identidade comum; nome igual ou coordenada coincidente não prova duplicidade.
6. **Validação:** preencher evidência verificável, método, data e revisor por linha, e inspecionar visualmente o mapa com os pontos corrigidos.
7. **Publicação:** somente promover uma versão quando cada registro tiver nome, classe e localização suficientemente justificados para a precisão **anunciada ao público**. Preservar os casos não demonstráveis como `pendente`, não como precisos.

## Proteção da base

- Branch de trabalho: `auditoria-publicacao-1237-2026-11-19`.
- Origem: `correcao-nomes-auditoria-2026-11-19`, v4.9 candidata com 8.610 feições.
- `main` e o site publicado permanecem intocados.
- **Não executar merge/publicação** apenas porque a auditoria automatizada passou. O sucesso significa que os números e vínculos foram verificados, não que os lugares foram confirmados.

## Observação sobre contagens anteriores

O relatório anterior da v4.9 apontou **563 alertas** conforme outra regra de auditoria. A nova verificação separa **566 prioridades críticas** incluindo POI não confiável, pontos de CEPs distintos sobrepostos, divergências com fonte e ausência de coordenada. As duas métricas não medem a mesma condição.
