# Painel de empreendimentos — demonstração

Busca por bairro, empreendimento, construtora, segmento, VGV, metragem e período. Todos os exemplos vêm de `demo_data.py`, uma fixture criada para esta apresentação; nenhuma planilha histórica é lida pelo aplicativo.

## Executar

Requer Python 3.13 (runtime validado em Windows). Crie um ambiente virtual e instale `python -m pip install -r requirements.lock`; execute `python -m streamlit run projeto1.py`. `requirements.txt` declara dependências diretas e o lock fixa também as transitivas. O lock não contém hashes de artefatos. A configuração padrão reconhecida fica em `.devcontainer/devcontainer.json`; CORS/XSRF permanecem ativos. Os testes locais foram executados em Windows com Python 3.13. Outras plataformas precisam de execução própria dos checks antes de implantação.

## Dados e envio

A variante pública usa dados fictícios, sem logotipo de organização, planilha real, telefone ou caixa de entrada real. Valores textuais são escapados antes dos cards HTML; links aceitam HTTPS e usam `noopener noreferrer`. A consulta do mapa é codificada como parâmetro, com escape de atributo.

O formulário valida localmente mensagens fictícias de até 2.000 caracteres e retorna `modo_demo`. A variante pública não implementa envio HTTP, não lê `SUGGESTION_ENDPOINT` e não registra mensagens como enviadas. Configuração de ambiente ou transporte passado à função não habilitam o envio. Os links de mapa abrem apenas quando acionados e usam os endereços fictícios da amostra.

Esta é uma demonstração, sem autorização para dados operacionais. Autenticação e autorização devem preceder qualquer inclusão de dados reais.

## Verificação

`python -m unittest discover -s tests -v` testa bloqueio de envio mesmo com configuração ou transporte fornecido, ausência de falso sucesso, mensagens inválidas, escape de HTML/links, filtros e interface que falha se tentar ler a planilha histórica ou enviar HTTP. `python -m pip check` verifica consistência das dependências. Telemetria de uso está desativada em `.streamlit/config.toml`.
