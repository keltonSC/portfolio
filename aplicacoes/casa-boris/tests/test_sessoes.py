from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
import os
import unittest
from unittest.mock import patch
from zipfile import ZipFile

import pandas as pd
from streamlit.testing.v1 import AppTest

from dados_sessao import ArquivoInvalido, desempenho_demo, importar_sessao, iniciar_sessao, ler_excel, validar_desempenho


def excel_bytes(frame):
    out = BytesIO()
    frame.to_excel(out, index=False, engine="openpyxl")
    return out.getvalue()


class DadosTest(unittest.TestCase):
    def test_sessoes_nao_compartilham_dataframe(self):
        a, b = {}, {}
        iniciar_sessao(a)
        iniciar_sessao(b)
        a["dados_desempenho"].loc[0, "Leads"] = 999
        a["dados_leads"].loc[0, "Nome do Lead"] = "Outra pessoa fictícia"
        self.assertEqual(b["dados_desempenho"].loc[0, "Leads"], 4)
        self.assertEqual(b["dados_leads"].loc[0, "Nome do Lead"], "Pessoa fictícia A")

    def test_upload_em_memoria_nao_sobrescreve_arquivo_ou_outra_sessao(self):
        a, b = {}, {}
        iniciar_sessao(a)
        iniciar_sessao(b)
        frame = desempenho_demo()
        frame.loc[0, "Leads"] = 10
        content = excel_bytes(frame)
        old_cwd = Path.cwd()
        with TemporaryDirectory() as tmp:
            try:
                os.chdir(tmp)
                self.assertTrue(importar_sessao(a, "desempenho", content))
                self.assertEqual(list(Path(tmp).iterdir()), [])
            finally:
                os.chdir(old_cwd)
        self.assertEqual(a["dados_desempenho"].loc[0, "Leads"], 10)
        self.assertEqual(b["dados_desempenho"].loc[0, "Leads"], 4)
        a["dados_desempenho"].loc[0, "Leads"] = 11
        self.assertFalse(importar_sessao(a, "desempenho", content))
        self.assertEqual(a["dados_desempenho"].loc[0, "Leads"], 11)

    def test_upload_invalido_preserva_dados_anteriores(self):
        state = {}
        iniciar_sessao(state)
        before = state["dados_desempenho"].copy(deep=True)
        for content in [b"nao e excel", excel_bytes(pd.DataFrame({"Outra": [1]}))]:
            with self.assertRaises(ArquivoInvalido):
                importar_sessao(state, "desempenho", content)
            pd.testing.assert_frame_equal(state["dados_desempenho"], before)
        self.assertNotIn("upload_desempenho_hash", state)

    def test_limites_tamanho_expansao_e_linhas(self):
        with self.assertRaises(ArquivoInvalido):
            ler_excel(b"x" * (5 * 1024 * 1024 + 1))
        zipped = BytesIO()
        with ZipFile(zipped, "w") as archive:
            archive.writestr("[Content_Types].xml", b"x" * (25 * 1024 * 1024 + 1), compress_type=8)
        with self.assertRaises(ArquivoInvalido):
            ler_excel(zipped.getvalue())
        with self.assertRaises(ArquivoInvalido):
            validar_desempenho(pd.concat([desempenho_demo()] * 2001, ignore_index=True))

    def test_validacao_datas_numeros_e_copia(self):
        for column, value in [("Data", "invalida"), ("Leads", -1), ("Leads", 0.5), ("Leads", float("inf")), ("Leads", 1e30), ("Investimento (R$)", float("nan"))]:
            frame = desempenho_demo().astype({column: "object"})
            frame.loc[0, column] = value
            with self.assertRaises(ArquivoInvalido):
                validar_desempenho(frame)
        original = desempenho_demo()
        result = validar_desempenho(original)
        result.loc[0, "Leads"] = 20
        self.assertEqual(original.loc[0, "Leads"], 4)

    def test_edicao_recalcula_cpl_e_sem_leads_nao_inventa_taxa(self):
        edited = desempenho_demo()
        edited.loc[0, ["Investimento (R$)", "Leads", "CPL (R$)"]] = [240, 8, 999]
        edited.loc[1, ["Investimento (R$)", "Leads", "CPL (R$)"]] = [150, 0, 0]
        result = validar_desempenho(edited)
        self.assertEqual(result.loc[0, "CPL (R$)"], 30)
        self.assertTrue(pd.isna(result.loc[1, "CPL (R$)"]))
        self.assertEqual(edited.loc[0, "CPL (R$)"], 999)
        pd.testing.assert_frame_equal(validar_desempenho(result), result)

    def test_mapeamento_leads_sem_arquivo_comum(self):
        frame = pd.DataFrame({"Data Primeiro Cadastro": ["2026-01-01", "2026-01-02"], "Nome": ["Pessoa teste A", "Pessoa teste B"], "Situação": ["Novo", "Novo"], "Data da última alteração de situação": ["2026-01-02", "2026-01-03"], "Corretor": ["Responsável fictício", None], "Momento do Lead": [None, "Teste"]})
        state = {}
        self.assertTrue(importar_sessao(state, "leads", excel_bytes(frame)))
        self.assertEqual(state["dados_leads"].iloc[1]["Responsável"], "Responsável fictício")
        self.assertEqual(state["dados_leads"].iloc[0]["Comentário"], "")


class AppTestCase(unittest.TestCase):
    def test_fluxo_inicial_ficticio_sem_leitura_de_disco(self):
        with patch("pandas.read_excel", side_effect=AssertionError("Leitura de disco não permitida no início")):
            app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "CasaBoris.py"), default_timeout=30).run()
            self.assertEqual(len(app.exception), 0)
            self.assertEqual(next(metric.value for metric in app.metric if metric.label == "Leads gerados"), "30")
            app.date_input(key="inicio").set_value(pd.Timestamp("2027-01-01").date()).run()
            self.assertEqual(len(app.exception), 0)
            self.assertIn("A data inicial", app.error[0].value)

    def test_duas_sessoes_streamlit_isoladas(self):
        a = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "CasaBoris.py"), default_timeout=30).run()
        b = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "CasaBoris.py"), default_timeout=30).run()
        changed = a.session_state["dados_desempenho"].copy(deep=True)
        changed.loc[0, "Leads"] = 40
        a.session_state["dados_desempenho"] = changed
        a.run()
        self.assertEqual(next(metric.value for metric in a.metric if metric.label == "Leads gerados"), "66")
        self.assertEqual(next(metric.value for metric in b.metric if metric.label == "Leads gerados"), "30")


if __name__ == "__main__":
    unittest.main()
