"""Validação local para a variante pública. Nenhum envio HTTP é implementado."""
MAX_MESSAGE = 2000


def enviar_sugestao(endpoint, mensagem, state, *, post=None):
    # Compatibility parameters are deliberately ignored: no config enables sending.
    # Never call the supplied transport or modify state as if delivery had occurred.
    if not isinstance(mensagem, str):
        return "invalida"
    message = mensagem.strip()
    if not message or len(message) > MAX_MESSAGE:
        return "invalida"
    return "modo_demo"
