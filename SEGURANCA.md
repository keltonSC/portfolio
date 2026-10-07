# Segurança e manutenção das demonstrações

Este portfólio apresenta práticas e decisões verificáveis. Um estudo de caso não comprova que toda a infraestrutura original está atualizada ou protegida.

## Critérios de preparação

- Usar dados fictícios e publicar somente arquivos selecionados; manter credenciais, bases de clientes, mídia privada e registros internos fora do repositório.
- Validar entradas, limitar consultas e separar autenticação de autorização. Senhas compartilhadas precisam evoluir para identidades individuais quando há dados pessoais ou diferentes níveis de acesso.
- Conferir permissões no backend e no banco; filtros da interface não são controles de acesso.
- Escapar conteúdo vindo de dados externos antes de inseri-lo na página e revisar políticas de conteúdo e origens permitidas.
- Manter dependências reproduzíveis e revisar atualizações, compatibilidade e alertas com fontes oficiais. Versão antiga, isoladamente, não comprova vulnerabilidade.
- Testar regressões e cenários negativos em ambiente isolado antes de alterar produção. Registrar falhas sem dados pessoais ou segredos.

## Estado desta revisão

As cópias selecionadas foram revisadas e executadas com fixtures, incluindo cenários negativos de validação, isolamento de sessões, renderização de texto hostil, exportação e transporte HTTP. O coordenador teve 25 testes aprovados e a demo de KPIs teve 4. Os aplicativos Python possuem suítes próprias e dependências fixadas nas respectivas pastas.

As demonstrações não precisam de acesso ao CRM ou banco. Antes de colocar código operacional em uso, configurar identidade e autorização no servidor, restringir escopo no banco, substituir credenciais comprometidas e testar o ambiente real. A revisão não realizou pentest ou rotação de credenciais. Remover um arquivo da versão atual não elimina cópias anteriores nem revoga seu conteúdo.

Achados operacionais e caminhos sensíveis permanecem em relatório privado. A presença de recomendações nesta página não significa que as correções já foram implantadas. Demonstrações online com dados reais precisam de uma versão sanitizada antes de compartilhamento aberto.

## Referências de verificação

- [OWASP ASVS](https://owasp.org/projects/asvs): requisitos para avaliar controles de aplicações.
- [Supabase — proteger a API](https://supabase.com/docs/guides/api/securing-your-api): permissões, schemas expostos e políticas de acesso.
- [GitHub — remover dados sensíveis](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository): tratamento de credenciais e histórico.

Data da revisão: 07/10/2026. Não há certificação ou garantia de ausência de vulnerabilidades.
