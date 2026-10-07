# Coordenador de seis papéis para planejamento audiovisual

Demonstrador em Node.js que organiza briefing, referências e fatos em um fluxo de planejamento: catalogador, roteirista, diretor, produtor, editor e revisor. O coordenador valida contratos JSON, preserva a origem dos fatos e controla dependências entre as etapas.

O exemplo é fictício. Os caminhos `fixture://` descrevem referências de teste; não apontam para mídia real.

## Tecnologias

Node.js, módulos ECMAScript, APIs nativas de arquivos e SHA-256, contratos JSON e `node:test`. Não há dependências externas, serviço em segundo plano ou API de IA conectada. Use Node.js 22 ou superior.

## Executar

Abra um terminal nesta pasta. Os caminhos abaixo são relativos a ela:

```sh
node --test tests/pipeline.test.mjs
node pipeline.mjs init examples/imovel-demo.json
node pipeline.mjs prompt piloto-local-001
node pipeline.mjs schema catalogador
node pipeline.mjs status piloto-local-001
```

`prompt` apresenta instruções, contexto e contrato da próxima etapa. Uma pessoa ou um assistente externo prepara a resposta e salva um JSON local, por exemplo `resposta-catalogador.json`. O coordenador não produz essa resposta automaticamente. Inclua os valores atuais de `job_id` e `input_digest` apresentados pelo prompt.

```sh
node pipeline.mjs accept piloto-local-001 resposta-catalogador.json
node pipeline.mjs prompt piloto-local-001
node pipeline.mjs status piloto-local-001
```

Repita `prompt` e `accept` em ordem até a revisão. O estado e o histórico ficam em `runs/`, criado somente durante o uso e ignorado pelo Git. Não reinicialize um ID existente: crie uma cópia do exemplo com um ID novo para outro trabalho.

Para refazer uma resposta já aceita, use a etapa correspondente:

```sh
node pipeline.mjs revise piloto-local-001 roteirista
node pipeline.mjs prompt piloto-local-001
```

Uma revisão invalida a etapa indicada e suas dependentes, preservando o histórico. `needs_input` bloqueia o avanço até a resolução da pendência e uma revisão explícita. Cada papel aceita no máximo três entregas por trabalho.

## O que é validado

- IDs únicos, referências existentes e correspondência dos fatos com a entrada.
- Ordem das seis etapas e digest do contexto para rejeitar respostas antigas.
- Soma de durações, continuidade da timeline e preservação do texto entre roteiro e edição.
- Declaração de simulação para geração por referência e distinção entre planejamento e execução.
- Revisão com verificações factuais, de referências e de duração.

Os 25 testes usam dados fictícios e pastas temporárias. Verificam contratos e transições, incluindo rejeições de traversal, fatos alterados, execução inventada e aprovação de vídeo sem render.

## Limites

O único modo é `planning`. Uma execução completa pode chegar a `plan_approved`; `video_produced` e `video_approved` permanecem `false`. O pacote não renderiza, não analisa cenas, não ouve áudio, não lê o Drive e não publica materiais.

As verificações automáticas não detectam toda afirmação falsa em texto livre nem medem qualidade criativa. Uma futura produção exigiria ferramentas, mídia autorizada e avaliação dos arquivos reais. Mantenha credenciais, dados de clientes, respostas privadas e mídias reais fora deste demonstrador.
