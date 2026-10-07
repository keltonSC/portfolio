# Produção audiovisual e verificação temporal

## Problema

Uma exportação pode ter codec e duração corretos e ainda apresentar locução duplicada, fala fora de posição ou legendas que atravessam cortes. Verificar apenas a timeline planejada não comprova o conteúdo do MP4 entregue.

## Solução desenvolvida

Fluxo local de montagem de vídeos verticais e auditoria técnica do arquivo exportado. A composição utiliza fontes rastreáveis, uma locução, uma instrumental e legendas associadas às falas. As verificações comparam o áudio decodificado da entrega às fontes, procuram ocorrências repetidas e avaliam pausas e posição temporal.

As revisões preservam versões anteriores e registram falhas, inclusive quando o áudio passa e as legendas precisam de correção. Inspeção de quadros e validação matemática permanecem distintas da avaliação audiovisual humana.

## Tecnologias

Node.js, Python, FFmpeg/ffprobe, NumPy, legendas ASS, manifests e hashes SHA-256.

## Estado e limites

Fluxo aplicado a pilotos internos, com exportações e auditorias técnicas registradas no ambiente original. Os scripts ainda dependem de materiais e parâmetros específicos desses pilotos.

Análise de quadros, correlação de áudio e checks de formato não substituem reprodução contínua, escuta, avaliação de naturalidade ou aprovação de uma peça. As mídias e as vozes dos pilotos não acompanham esta ficha; sua exibição dependeria das permissões correspondentes.

Este caso apresenta o método de verificação. Não inclui acervo de clientes, vídeos privados ou alegações de resultados comerciais.
