# Aplicações Python

Versões selecionadas e revisadas em 07/10/2026, acompanhadas de exemplos fictícios e testes. Arquivos comerciais, marcas, credenciais e históricos operacionais ficam fora deste repositório. Cada pasta documenta instalação, execução e limites.

## Gerador de PDF

**Problema:** preparar folhetos com fotos e informações em formato consistente.

**Implementação:** aplicação com capa, envio de fotos em lote e marca d’água configurável. Produz PDF único, folhetos individuais e ZIP. Valida JPEG/PNG por conteúdo e limita tamanho, pixels e quantidade; normaliza orientação, converte para sRGB e remove metadados de origem das imagens processadas.

**Tecnologias:** Python, Streamlit, Pillow e ReportLab.

**Evidência:** [código selecionado, dependências fixadas e testes](../aplicacoes/gerador-pdf/README.md). Testes com imagens geradas verificam modos de exportação, rejeição de arquivos inválidos, metadados e interface.

**Limite:** a marca de exemplo é genérica. Usar apenas imagens e marcas autorizadas; os testes não avaliam direitos de uso ou qualidade visual de material de terceiros.

## Casa Boris

**Problema:** transformar planilhas de campanhas e leads em indicadores de acompanhamento.

**Implementação:** painel com período, investimento, leads, CPL e evolução diária. Importação, mapeamento e edição de tabelas usam dados em memória por sessão, com validação de schema, datas e números. Uploads de visitantes diferentes não compartilham nomes de arquivo em disco. O CPL acompanha alterações de investimento e leads.

**Tecnologias:** Python, Streamlit, Pandas, Matplotlib e OpenPyXL.

**Evidência:** [código selecionado e testes de sessões](../aplicacoes/casa-boris/README.md). Fixtures substituem as planilhas comerciais.

**Limite:** este exemplo não possui contas, persistência ou gestão de permissões de uma operação comercial. Os indicadores fictícios não representam resultados de campanhas reais.

## Painel de lançamentos

**Problema:** consultar registros com valores, datas e metragens em formatos diferentes.

**Implementação:** normalização, filtros e detalhes por registro. Versões públicas carregam exclusivamente dados fictícios e escapam texto externo na renderização. CORS e proteção XSRF ficam ativos; sugestões são validadas localmente, sem envio externo.

**Tecnologias:** Python, Streamlit e Pandas.

**Evidência:** [versão LCI](../aplicacoes/lancamentos-lci/README.md) e [versão LC](../aplicacoes/lancamentos-lc/README.md), com testes de normalização, HTML hostil, entradas e interface.

**Limite:** nenhum empreendimento, endereço, condição ou disponibilidade do exemplo representa uma oferta comercial real.

## Relatório de KPIs

**Problema:** separar uma demonstração aberta do acesso aos indicadores operacionais de CRM.

**Implementação:** inicia com agregados fictícios sem chamadas HTTP. A camada operacional exige ativação explícita, identidade verificada, sessão válida e allowlist no servidor antes de consultar dados. Credenciais trafegam apenas em cabeçalhos de requests HTTPS para destinos restritos, com timeout e erros sanitizados.

**Evidência:** [código selecionado, instruções e testes](../aplicacoes/relatorio-kpis/README.md).

**Limite:** autenticação e serviços de produção não estão configurados nesta demonstração. A allowlist autoriza o conjunto de dados inteiro; segregação por equipe exige implementação específica no servidor e no banco.
