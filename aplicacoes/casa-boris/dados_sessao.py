"""Dados fictícios e uploads isolados: nenhuma planilha é gravada no disco."""
from hashlib import sha256
from io import BytesIO
from math import isfinite
from zipfile import ZipFile

import pandas as pd

MAX_UPLOAD_BYTES = 5 * 1024 * 1024
MAX_EXPANDED_BYTES = 25 * 1024 * 1024
MAX_ROWS = 10_000
DESEMPENHO_COLUMNS = ["Data", "Investimento (R$)", "Leads", "CPL (R$)"]
LEADS_COLUMNS = ["Data Primeiro Cadastro", "Nome", "Situação", "Data da última alteração de situação", "Corretor", "Momento do Lead"]


class ArquivoInvalido(ValueError):
    pass


def desempenho_demo():
    investimento = [120.0, 150.0, 130.0, 160.0, 140.0]
    leads = [4, 6, 5, 8, 7]
    return pd.DataFrame({"Data": pd.date_range("2026-01-05", periods=5), "Investimento (R$)": investimento, "Leads": leads, "CPL (R$)": [v / n for v, n in zip(investimento, leads)]})


def leads_demo():
    return pd.DataFrame({"Data do Lead": [pd.Timestamp("2026-01-05").date()] * 3, "Nome do Lead": ["Pessoa fictícia A", "Pessoa fictícia B", "Pessoa fictícia C"], "Status de Atendimento": ["Novo", "Em atendimento", "Concluído"], "Último Contato": [pd.Timestamp("2026-01-06").date()] * 3, "Responsável": ["Responsável fictício 1"] * 3, "Comentário": ["Demonstração sem contato real"] * 3})


def iniciar_sessao(state):
    if "dados_desempenho" not in state:
        state["dados_desempenho"] = desempenho_demo()
    if "dados_leads" not in state:
        state["dados_leads"] = leads_demo()


def ler_excel(data):
    if not data or len(data) > MAX_UPLOAD_BYTES:
        raise ArquivoInvalido("Envie um XLSX de até 5 MB.")
    try:
        with ZipFile(BytesIO(data)) as archive:
            entries = archive.infolist()
            if len(entries) > 1000 or sum(entry.file_size for entry in entries) > MAX_EXPANDED_BYTES:
                raise ArquivoInvalido("A planilha excede o limite de conteúdo descompactado.")
            if "[Content_Types].xml" not in archive.namelist():
                raise ArquivoInvalido("O arquivo não é uma planilha XLSX válida.")
        frame = pd.read_excel(BytesIO(data), engine="openpyxl", engine_kwargs={"keep_links": False}, nrows=MAX_ROWS + 1)
    except ArquivoInvalido:
        raise
    except Exception as exc:
        raise ArquivoInvalido("Não foi possível ler a planilha XLSX.") from exc
    if frame.empty or len(frame) > MAX_ROWS:
        raise ArquivoInvalido("Use uma planilha com 1 a 10.000 linhas.")
    return frame


def validar_desempenho(frame):
    if not set(DESEMPENHO_COLUMNS).issubset(frame.columns) or frame.empty or len(frame) > MAX_ROWS:
        raise ArquivoInvalido("Confira as colunas Data, Investimento (R$), Leads e CPL (R$).")
    result = frame[DESEMPENHO_COLUMNS].copy(deep=True)
    result["Data"] = pd.to_datetime(result["Data"], errors="coerce", format="mixed")
    if result["Data"].isna().any():
        raise ArquivoInvalido("Todas as linhas precisam de uma data válida.")
    for column in ["Investimento (R$)", "Leads"]:
        result[column] = pd.to_numeric(result[column], errors="coerce")
        if not result[column].map(isfinite).all() or (result[column] < 0).any():
            raise ArquivoInvalido("Investimento e leads precisam ser números não negativos.")
    if (result["Leads"] % 1 != 0).any():
        raise ArquivoInvalido("A quantidade de leads precisa ser inteira.")
    if (result["Leads"] >= 2**63).any():
        raise ArquivoInvalido("A quantidade de leads excede o limite numérico aceito.")
    result["Leads"] = result["Leads"].astype(int)
    # Recalculate after every import/edit: stale spreadsheet rates must not survive.
    result["CPL (R$)"] = result["Investimento (R$)"].div(result["Leads"].where(result["Leads"] > 0))
    return result


def mapear_leads(frame):
    if not set(LEADS_COLUMNS).issubset(frame.columns):
        raise ArquivoInvalido("Confira as colunas do modelo de leads descrito no README.")
    cadastro = pd.to_datetime(frame["Data Primeiro Cadastro"], errors="coerce", format="mixed")
    contato = pd.to_datetime(frame["Data da última alteração de situação"], errors="coerce", format="mixed")
    if cadastro.isna().any() or contato.isna().any():
        raise ArquivoInvalido("As datas de cadastro e último contato precisam ser válidas.")
    return pd.DataFrame({"Data do Lead": cadastro.dt.date, "Nome do Lead": frame["Nome"].fillna("").astype(str), "Status de Atendimento": frame["Situação"].fillna("Sem status").astype(str), "Último Contato": contato.dt.date, "Responsável": frame["Corretor"].ffill().fillna("Sem responsável").astype(str), "Comentário": frame["Momento do Lead"].fillna("").astype(str)})


def importar_sessao(state, kind, data):
    if kind not in {"desempenho", "leads"}:
        raise ArquivoInvalido("Tipo de planilha inválido.")
    digest = sha256(data).hexdigest()
    if state.get(f"upload_{kind}_hash") == digest:
        return False
    frame = ler_excel(data)
    normalized = validar_desempenho(frame) if kind == "desempenho" else mapear_leads(frame)
    state[f"dados_{kind}"] = normalized.copy(deep=True)
    state[f"upload_{kind}_hash"] = digest
    return True
