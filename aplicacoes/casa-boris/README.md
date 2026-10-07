# Relatório de marketing — demonstração

Painel com visão geral, agenda, desempenho, acompanhamento de leads, insights e planejamento. A apresentação inicial usa somente pessoas e métricas inventadas.

## Executar

Requer Python 3.13 (runtime validado em Windows). Crie um ambiente virtual e instale `python -m pip install -r requirements.lock`; inicie com `python -m streamlit run CasaBoris.py`. `requirements.txt` declara dependências diretas, e o lock fixa as versões diretas/transitivas resolvidas. O lock não contém hashes de artefatos. Os testes locais foram executados em Windows com Python 3.13. Outras plataformas precisam de execução própria dos checks antes de implantação.

## Dados e privacidade

Uploads XLSX ficam em `st.session_state` da sessão, sem arquivos comuns no disco nem cache compartilhado de dados enviados. Reiniciar/recarregar a sessão pode descartar alterações. Use somente dados fictícios nesta demonstração pública; operação real precisa de autenticação, autorização e armazenamento por proprietário.

As planilhas precisam de 1 a 10.000 linhas, no máximo 5 MB compactados e 25 MB de conteúdo descompactado. O parser usa openpyxl com defusedxml instalado e sem preservação de links externos. Formatos, datas e números inválidos são rejeitados antes da substituição dos dados da sessão; o erro mostrado não reproduz conteúdo ou caminhos internos.

Modelo de desempenho: `Data`, `Investimento (R$)`, `Leads`, `CPL (R$)`. Modelo de leads: `Data Primeiro Cadastro`, `Nome`, `Situação`, `Data da última alteração de situação`, `Corretor`, `Momento do Lead`.

O valor de CPL informado na planilha é ignorado e recalculado como investimento dividido por leads após cada importação ou edição. Uma linha sem leads fica sem taxa (`NaN`) e o indicador do período mostra “—” quando não há denominador; o painel não apresenta um custo por lead fictício de zero. O indicador do período usa a razão das somas.

## Verificação

`python -m unittest discover -s tests -v` cobre sessões independentes, upload sem gravação, limites, preservação após erro, mapeamento e a interface Streamlit com dados sintéticos. `python -m pip check` verifica consistência das dependências. CORS e proteção XSRF permanecem habilitados em `.streamlit/config.toml`; telemetria de uso está desativada.
