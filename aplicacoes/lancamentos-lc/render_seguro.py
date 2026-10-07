from html import escape
from urllib.parse import urlencode, urlsplit


def texto(valor):
    return escape(str(valor), quote=True)


def link_https(valor):
    try:
        parsed = urlsplit(str(valor))
        if parsed.scheme == "https" and parsed.hostname and not parsed.username and not parsed.password:
            return escape(str(valor), quote=True)
    except ValueError:
        pass
    return ""


def link_mapa(endereco, bairro):
    query = urlencode({"api": 1, "query": f"{endereco}, {bairro}"})
    return escape("https://www.google.com/maps/search/?" + query, quote=True)
