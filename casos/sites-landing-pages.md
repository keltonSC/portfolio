# Sites e landing pages — protótipos de interface

## Problema

Uma apresentação digital precisa organizar proposta de valor, conteúdo, navegação e chamadas para ação de forma clara em diferentes tamanhos de tela. Protótipos ajudam a avaliar essa estrutura antes de conectar formulários, serviços e conteúdo definitivo.

## Solução

Conjunto de protótipos com páginas de apresentação, catálogo, detalhe e contato, além de landing pages organizadas em seções. Os fontes contêm navegação, estilos responsivos, metadados de página e conteúdo configurável em templates.

Os formulários observados são demonstrativos. Não há comprovação nesta revisão de envio real, conexão com CRM ou funcionamento de uma operação comercial.

## Arquitetura

Há duas abordagens observadas:

- **Site estático:** páginas HTML, folha de estilos e comportamento de interface em JavaScript.
- **Página servida por aplicação:** rota FastAPI, templates Jinja2 e arquivos estáticos de CSS/JavaScript; o servidor fornece o conteúdo para o template.

**Tecnologias observadas:** HTML, CSS, JavaScript, Python, FastAPI e Jinja2.

## Decisões

- Distribuir o conteúdo entre apresentação, catálogo, detalhe e contato quando a navegação exige várias páginas.
- Usar seções e chamadas para ação na apresentação de uma landing page.
- Definir breakpoints de CSS para reorganizar componentes em telas menores.
- Manter conteúdo demonstrativo e formulários sem operação comercial durante a prototipagem.

## Entrega verificada

Em 07/10/2026 foram examinados fontes de páginas, estilos, templates e rotas. A implementação sustenta competências em estrutura de páginas, layout responsivo, organização de conteúdo e templates de servidor.

Uma prévia institucional local, documentada separadamente, já passou por verificação de interface em navegador, responsividade e navegação por teclado. Essa evidência histórica se limita à prévia inspecionada e não foi reexecutada nesta revisão.

Não houve publicação, nova avaliação visual no navegador, teste de envio, auditoria completa de acessibilidade ou medição de conversão nesta revisão. Marcas, conteúdo de terceiros, arquivos operacionais e resultados comerciais não acompanham esta ficha.

## Próximo passo

Preparar uma versão neutra com conteúdo fictício, validar a apresentação em telas diferentes e conferir navegação por teclado, contraste e formulários. A conexão de serviços reais deve incluir validação no servidor, tratamento de dados pessoais e controles contra abuso.
