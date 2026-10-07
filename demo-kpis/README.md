# Dashboard de KPIs — demonstração pública

Campanhas, produtos, canais, filtros e funil conectados em um painel estático. Todos os 12 registros, nomes e resultados são fictícios; não há dados de clientes, contatos, credenciais ou conexões externas. A amostra apresenta decisões de interface e cálculo, sem alegar resultado comercial real ou segurança de uma implantação operacional.

JavaScript com módulos nativos, HTML sem handlers inline, CSS local e renderização com `textContent`/DOM. A CSP no HTML não permite scripts inline ou conexão de rede. Sem CDN, analytics ou dependências de runtime.

Sirva esta pasta por HTTP estático para carregar os módulos ES. `index.html` inicia a demonstração. A política no HTML protege scripts/conexões; o host também deve servir `_headers` ou o equivalente para bloquear frames e definir `nosniff`. `_headers` é uma convenção de alguns hosts e não é aplicada automaticamente pelo GitHub Pages. Nesse serviço, o bloqueio de enquadramento depende de uma camada que permita configurar os cabeçalhos HTTP.

Verificação local: `node --test tests/*.test.mjs`. Testa agregação, filtros e regressão contra HTML malicioso como nome/campanha/busca, com fixtures sintéticas. Não é um pentest de produção.
