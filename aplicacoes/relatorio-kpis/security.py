"""Fail-closed access and CRM transport. Never log credentials or response bodies."""
from __future__ import annotations

import math
import os
import re
import time
from collections.abc import Mapping

import requests

_PATHS = frozenset({"/api/cvio/lead", "/api/cvio/lead_tarefas", "/api/v1/comercial/leads/interacoes"})
_SUBDOMAIN = re.compile(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\Z")


class CRMError(RuntimeError):
    """A deliberately sanitized transport error."""


def live_enabled() -> bool:
    return os.environ.get("RELATORIO_LIVE_ENABLED") == "true"


def authorized(claims: Mapping, allowed_emails, *, now=None) -> bool:
    """Exact allowlist, verified identity and unexpired OIDC token, no domain matching."""
    if claims.get("is_logged_in") is not True or claims.get("email_verified") is not True:
        return False
    email = claims.get("email")
    if not isinstance(email, str) or not isinstance(allowed_emails, (list, tuple)):
        return False
    allowlist = {item.strip().casefold() for item in allowed_emails if isinstance(item, str) and item.strip()}
    if email.strip().casefold() not in allowlist:
        return False
    expiry = claims.get("exp")
    if isinstance(expiry, bool) or not isinstance(expiry, (int, float)) or not math.isfinite(expiry):
        return False
    return expiry > (time.time() if now is None else now)


def clear_private_state(st) -> None:
    for key in list(st.session_state):
        if str(key).startswith(("cv_", "CV_", "inter_", "_authorized_identity", "__leads_diag__")):
            del st.session_state[key]


def require_authorized_user(st) -> None:
    """Call before reading service secrets or loading any live data."""
    if not live_enabled():
        clear_private_state(st)
        st.info("Acesso operacional desabilitado. Use a demonstração com dados fictícios.")
        st.stop()
    try:
        access = st.secrets.get("access", {})
        allowed_emails = access.get("allowed_emails", [])
        claims = dict(st.user)
    except Exception:
        claims, allowed_emails = {}, []
    if not authorized(claims, allowed_emails):
        clear_private_state(st)
        st.warning("Acesso restrito a identidades verificadas e autorizadas.")
        if claims.get("is_logged_in") is not True and st.button("Entrar", key="security_login"):
            try:
                st.login()
            except Exception:
                st.error("Login indisponível. O administrador deve conferir a configuração de autenticação.")
        st.stop()
    identity = claims["email"].strip().casefold()
    if st.session_state.get("_authorized_identity") != identity:
        clear_private_state(st)
        st.session_state["_authorized_identity"] = identity
    if st.sidebar.button("Sair", key="security_logout"):
        clear_private_state(st)
        st.logout()
        st.stop()


def crm_json(session, subdomain, path, email, token, params):
    """One HTTPS request: credentials only in headers, no redirects or fallback."""
    if not isinstance(subdomain, str) or not _SUBDOMAIN.fullmatch(subdomain) or path not in _PATHS:
        raise CRMError("Configuração de endpoint inválida.")
    if not isinstance(email, str) or not email or not isinstance(token, str) or not token:
        raise CRMError("Credenciais do serviço não configuradas.")
    if any(c in email + token for c in ("\r", "\n")):
        raise CRMError("Credenciais do serviço inválidas.")
    allowed_params = {"limit", "offset", "pagina"}
    if not isinstance(params, dict) or set(params) - allowed_params:
        raise CRMError("Parâmetros de consulta inválidos.")
    for key, value in params.items():
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise CRMError("Parâmetros de consulta inválidos.")
        if (key == "limit" and not 1 <= value <= 5000) or (key == "pagina" and not 1 <= value <= 1000) or value > 100000:
            raise CRMError("Limite de consulta excedido.")
    url = f"https://{subdomain}.cvcrm.com.br{path}"
    try:
        response = session.get(url, headers={"email": email, "token": token}, params=dict(params), timeout=(5, 30), allow_redirects=False)
        if not 200 <= response.status_code < 300:
            raise CRMError("O serviço não concluiu a consulta.")
        payload = response.json()
        if not isinstance(payload, (dict, list)):
            raise CRMError("Resposta do serviço inválida.")
        return response.status_code, payload
    except CRMError:
        raise
    except (requests.RequestException, ValueError, TypeError):
        raise CRMError("Falha de comunicação com o serviço.") from None
