# Relatório de KPIs

Aplicação Streamlit para análise de funil. A execução padrão usa exclusivamente agregados fictícios e não consulta serviços externos.

```powershell
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
.venv/Scripts/python -m streamlit run streamlit_app.py
```

## Operação restrita

Antes de habilitar `RELATORIO_LIVE_ENABLED=true`, o administrador precisa configurar OIDC no secret store do servidor, uma lista explícita `access.allowed_emails`, credenciais CRM rotacionadas, endpoint permitido e HTTPS com acesso restrito. Exige identidade com e-mail verificado e claim `exp` válido. A allowlist concede acesso ao conjunto completo de dados disponível à identidade de serviço; ela não implementa perfis por equipe. Se houver perfis diferentes, implementar autorização por registro no backend antes de conceder acesso.

Não coloque valores reais em `secrets.example.toml`, Git, URLs ou mensagens. O código nega acesso sem configuração e remove estado privado ao mudar a identidade ou sair. O transporte usa cabeçalhos, timeout, status validado, rejeita redirects e não exibe corpo/erro bruto do provedor. OIDC e conectividade real precisam de validação no ambiente de implantação; testes fictícios não comprovam a operação do CRM.

## Verificação

`python -m unittest discover -s tests -v` cobre autorização, expiração e transporte sem chamadas reais. A remoção de um arquivo no commit atual não limpa o histórico nem revoga credenciais já expostas. O histórico original deve permanecer privado enquanto o responsável confirma a contenção. Documentação: [Streamlit Auth](https://docs.streamlit.io/develop/concepts/connections/authentication), [GitHub — dados sensíveis](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository).

## Controles desta revisão

O endpoint do tenant do CRM vem exclusivamente da configuração do servidor, sem edição no navegador. A sessão HTTP não faz retry automático. Dados privados ficam na sessão da aplicação, sem cache global de consultas; a troca de identidade/logout elimina DataFrames e diagnósticos privados. Diagnósticos não incluem amostras de registros, e exportações XLSX neutralizam fórmulas em textos não confiáveis. CORS/XSRF ficam ativos e telemetria de uso desativada.

Não existe upload de planilha ativo nesta variante. O único caminho XLSX é a exportação de dados já carregados após a autenticação do modo restrito. A demonstração pública usa somente valores fictícios e não lê segredos ou datasets históricos.

A consulta legada de leads/tarefas usa o primeiro lote do serviço; não comprova coleta de todas as páginas. Valide completude e regras de negócio antes de uso operacional. A suíte usa mocks/fixtures: não comprova login OIDC ou autorização por registro implantados. Modo operacional e OIDC não estão configurados nesta entrega. A allowlist autoriza o conjunto de dados da identidade de serviço, sem perfis por equipe.

`requirements.in` contém as dependências diretas; `requirements.txt` é o lock com hashes gerado e verificado para CPython 3.13 em Windows. Instale com `python -m pip install --require-hashes -r requirements.txt`, e execute `python -m pip check` e `python -m unittest discover -s tests -v`. Outras plataformas devem executar os mesmos checks antes de implantação.
