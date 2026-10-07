# Portfólio de projetos | Kelton Pereira

Automação, IA aplicada e ferramentas para o mercado imobiliário.

Reúno aqui projetos para organizar informações, transformar planilhas em aplicações, preparar documentos e coordenar produção audiovisual. Cada caso apresenta o problema atendido, a implementação e os limites da verificação.

[Apresentação no Notion](https://app.notion.com/p/3f2f4f87c8968000af3fd129fd1f7536) · [Perfil GitHub](https://github.com/keltonSC)

## Projetos em destaque

| Projeto | Aplicação | Tecnologias | Acesso |
|---|---|---|---|
| Coordenador de seis papéis | Briefings, contratos JSON, dependências e revisão de planos audiovisuais | Node.js, JavaScript, SHA-256, node:test | [Código e exemplo fictício](demo-agentes/README.md) |
| Gerador de PDF | Folhetos de imóveis com fotos e marca d’água | Python, Streamlit, Pillow, ReportLab | [Ficha](casos/aplicacoes-python.md#gerador-de-pdf) · [Repositório](https://github.com/keltonSC/Gerador-de-PDF) |
| Casa Boris | Painel de campanhas e leads a partir de planilhas | Python, Streamlit, Pandas, Matplotlib | [Ficha](casos/aplicacoes-python.md#casa-boris) · [Repositório](https://github.com/keltonSC/Casa-Boris) |
| Painel de lançamentos | Consulta de empreendimentos com filtros e normalização de dados | Python, Streamlit, Pandas, Requests | [Ficha](casos/aplicacoes-python.md#painel-de-lançamentos) · [Repositório](https://github.com/keltonSC/Lancamentos-LCI) |
| Catálogo documental e MCP | Recuperação textual com referências, escopo e validade de snapshots | Node.js, PostgreSQL, SDK MCP, Zod | [Estudo de caso](casos/catalogo-rag-mcp.md) |
| Produção audiovisual e QA | Montagem local e verificação temporal de voz e legendas | Node.js, Python, FFmpeg, NumPy | [Estudo de caso](casos/producao-audiovisual-qa.md) |

## Demonstrador executável

O coordenador de seis papéis acompanha este repositório com exemplo inteiramente fictício. O fluxo passa por catalogador, roteirista, diretor, produtor, editor e revisor. As transições validam a entrada de cada etapa e rejeitam fatos alterados, contexto desatualizado e execução de vídeo inventada.

```mermaid
flowchart LR
    A[Briefing e referências] --> B[Catalogador]
    B --> C[Roteirista]
    C --> D[Diretor]
    D --> E[Produtor]
    E --> F[Editor]
    F --> G[Revisor]
```

Requisito: Node.js 22 ou superior. Não há dependências externas a instalar.

```sh
node --test demo-agentes/tests/pipeline.test.mjs
node demo-agentes/pipeline.mjs init demo-agentes/examples/imovel-demo.json
node demo-agentes/pipeline.mjs prompt piloto-local-001
node demo-agentes/pipeline.mjs status piloto-local-001
```

O coordenador trabalha em modo `planning`: recebe respostas JSON preparadas por uma pessoa ou assistente e valida o plano. Não gera automaticamente respostas de IA nem renderiza vídeo. [Leia o fluxo completo](demo-agentes/README.md).

## Verificação e estado

- **Demonstrador:** 25 testes passaram na cópia portátil em 07/10/2026. Os testes cobrem contratos e transições; não medem qualidade criativa.
- **Aplicações Python:** capacidades verificadas por leitura do código público. Interface, integrações e exportações não foram executadas nesta preparação.
- **Catálogo/MCP e audiovisual:** estudos de caso da implementação original. Código operacional e mídia privada não acompanham estas fichas.

Os exemplos deste repositório são fictícios. A apresentação não contém bases de clientes, credenciais, históricos internos ou material de projetos confidenciais. Resultados comerciais e ganhos de tempo não foram medidos nesta preparação.
