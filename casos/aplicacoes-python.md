# Aplicações Python

Fichas preparadas em 07/10/2026 a partir de leitura estática do código público. Os aplicativos não foram executados nesta preparação. As descrições apresentam capacidades implementadas, sem atribuir resultados comerciais ou certificar integrações ativas.

## Gerador de PDF

**Problema:** preparar folhetos de imóveis com fotos e informações em um formato consistente.

**Implementação:** aplicação web com escolha de capa, envio de fotos em lote e marca d’água configurável em posição, tamanho, opacidade e margem. O código prevê PDF único, arquivos individuais e ZIP.

**Tecnologias:** Python, Streamlit, Pillow e ReportLab.

**Evidência:** [repositório](https://github.com/keltonSC/Gerador-de-PDF) e [código consultado](https://github.com/keltonSC/Gerador-de-PDF/blob/049aeb37c8330bfa51574524f8bcd4b30e50841d/PDFapp.py).

**Estado:** código disponível. Aparência e exportação dos folhetos não foram testadas nesta preparação. Uma demonstração deve utilizar imagens e marcas com permissão de uso.

## Casa Boris

**Problema:** transformar planilhas de campanhas e leads em indicadores de acompanhamento.

**Implementação:** painel com filtros por intervalo de datas, investimento total, quantidade de leads, custo por lead e evolução diária. O código também prevê importação, mapeamento e edição de tabelas e contagem por status de atendimento.

**Tecnologias:** Python, Streamlit, Pandas, Matplotlib e OpenPyXL.

**Evidência:** [repositório](https://github.com/keltonSC/Casa-Boris) e [código consultado](https://github.com/keltonSC/Casa-Boris/blob/d9466fead703a7b69745f2a1e4ee0face0b1fb38/CasaBoris.py).

**Estado:** código disponível. Aplicação e esquema das planilhas não foram executados ou validados nesta preparação. Demonstrações devem usar dados fictícios.

## Painel de lançamentos

**Problema:** consultar informações de empreendimentos a partir de uma planilha com campos em formatos diferentes.

**Implementação:** aplicação que normaliza valores de VGV, datas e listas de metragens e oferece filtros por bairro, empreendimento, construtora, segmento e período. Exibe a contagem dos itens selecionados e detalhes em painéis expansíveis.

**Tecnologias:** Python, Streamlit, Pandas e Requests.

**Evidência:** [repositório principal](https://github.com/keltonSC/Lancamentos-LCI) e [código consultado](https://github.com/keltonSC/Lancamentos-LCI/blob/32655e4cd1d846a2681b1d2e696021af06450ad1/projeto1.py). [Lancamentos-LC](https://github.com/keltonSC/Lancamentos-LC) é uma versão relacionada: o arquivo principal consultado era idêntico, sem afirmar igualdade de todo o histórico ou conteúdo dos repositórios.

**Estado:** código disponível. Planilhas comerciais, atualidade dos empreendimentos e aplicação não foram verificadas nesta preparação. O envio HTTP de comentários previsto no código não foi acionado; uma demonstração deve usar dados fictícios e desativar envios reais.
