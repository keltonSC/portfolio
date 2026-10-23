# CRM com Next.js e Supabase — projeto em desenvolvimento

## Problema

Organizar leads, responsáveis, situações do funil e próximos contatos em uma aplicação web, mantendo regras consistentes entre interface, integrações e banco.

## Solução observada

O [repositório público LC CRM](https://github.com/keltonSC/lc-crm) contém telas de lista e kanban de leads, detalhe e cadastro, tarefas, agenda e gestão de equipe. O acesso prevê convites com papel e equipe definidos pelo gestor.

## Arquitetura e decisões

- **Interface:** TypeScript, React e Next.js com App Router e Server Actions; estilos em Tailwind CSS.
- **Sessão:** clientes de Supabase separados para navegador e servidor, com verificação de identidade no servidor.
- **Domínio:** migrations de PostgreSQL concentram normalização, deduplicação, origem do lead e histórico de alterações.
- **Permissões:** políticas de acesso por papel e equipe, proteção de alterações do próprio perfil e views configuradas para respeitar a identidade de quem consulta.
- **Validação:** o repositório inclui testes SQL para regras do banco e instruções de execução local.

## Entrega verificada

Em 23/10/2026 foram examinados o README, a estrutura de arquivos, os manifestos e trechos de sessão e migrations do `main`, commit [`40e0ef9`](https://github.com/keltonSC/lc-crm/commit/40e0ef9f79b1ccb07b02ed10223401c1782f043d). Isso comprova a presença do código descrito, sem comprovar sua implantação ou o resultado de testes em produção.

A [PR #1 — distribuição automática de leads](https://github.com/keltonSC/lc-crm/pull/1) estava aberta nessa data. A roleta por equipe e corretor permanece uma alteração em revisão e não é apresentada como funcionalidade integrada ao `main`.

## Limites e próximos passos

O projeto está em desenvolvimento. Esta revisão não executou o CRM, seus testes SQL, um login real ou fluxos com dados de clientes. A qualidade operacional, a configuração do banco implantado e a hospedagem exigem validação própria.

Antes de ampliar o uso: revisar e atualizar dependências, automatizar as verificações de código e banco, concluir a revisão da distribuição e validar os perfis de acesso em ambiente de teste. Resultados comerciais e ganhos de produtividade ainda não foram medidos.
