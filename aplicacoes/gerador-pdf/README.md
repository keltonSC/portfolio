# Gerador de PDF e marca d'água

Aplicativo Streamlit para compor um folheto, aplicar marca d'água e exportar imagens em PDF, ZIP ou arquivos individuais. O processamento usa memória e não grava uploads no disco. As cópias exportadas aplicam a orientação EXIF, removem EXIF/GPS/XMP/comentários e convertem o perfil de cor válido para sRGB. Os originais não são alterados.

## Instalação e execução

Ambiente validado: Python 3.13 no Windows. Use um ambiente virtual separado:

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install --require-hashes -r requirements.txt
.venv\Scripts\python -m streamlit run PDFapp.py
```

A configuração efetiva fica em `.streamlit/config.toml`, com CORS e XSRF habilitados. `requirements.in` registra as dependências diretas e `requirements.txt` contém as versões transitivas e hashes resolvidos. Para testes, instale `requirements-dev.txt` com `--require-hashes` e execute `python -m unittest discover -s tests -v`. O lock foi gerado para Python 3.13; outros runtimes exigem instalação e validação próprias.

## Arquivos e limites

- JPEG e PNG estáticos: a extensão e o formato interno precisam corresponder. Outros decoders, arquivos incompletos e perfis de cor inválidos são rejeitados.
- Até 10 MiB, 16 megapixels e 8000 pixels por lado em cada imagem.
- Até 20 imagens, 50 MiB e 32 megapixels por lote, incluindo a capa no modo combinado. Saídas limitadas a 60 MiB.
- Os nomes exportados são genéricos e únicos, evitando replicar dados pessoais ou caminhos dos nomes originais.
- `logotopo.png` e `marcadagua.png` são recursos locais opcionais de identidade visual. Use somente material autorizado; o aplicativo não autoriza reutilizar uma marca. Sem arquivo de marca, o app usa uma marca genérica `DEMO`. Arquivos inválidos são rejeitados. O pacote público do portfólio não inclui marcas ou fotos reais.

O envio é limitado pelo Streamlit a 10 MiB por arquivo; os limites agregados são validados antes de processar o lote. Em uma implantação compartilhada, configure também limites de requisição, autenticação e retenção na infraestrutura. A aplicação não implementa gestão de usuários nem pode remover dados visíveis no conteúdo da foto ou digitados no folheto. Revise as imagens e o texto antes de publicar a saída. Não adicione uploads reais, segredos ou exportações ao repositório.

## Atualizações de segurança

Streamlit 1.65.0 e Pillow 12.3.0 incluem as correções dos advisories [GHSA-7p48-42j8-8846](https://github.com/streamlit/streamlit/security/advisories/GHSA-7p48-42j8-8846) e [GHSA-whj4-6x5x-4v2j](https://github.com/python-pillow/Pillow/security/advisories/GHSA-whj4-6x5x-4v2j). ReportLab permanece na versão 4.5.1 da série 4, validada com as exportações existentes. Os testes usam imagens e metadados sintéticos; não constituem um teste de produção ou garantia de ausência de todas as vulnerabilidades.

Para regenerar os locks com pip-tools 7.6.2:

```text
python -m piptools compile --generate-hashes --resolver=backtracking --no-emit-index-url --no-emit-trusted-host requirements.in
python -m piptools compile --generate-hashes --resolver=backtracking --no-emit-index-url --no-emit-trusted-host requirements-dev.in
```
