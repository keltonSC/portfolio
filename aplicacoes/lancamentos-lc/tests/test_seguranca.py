import os
from pathlib import Path
import tomllib
import unittest
from unittest.mock import Mock, patch

import requests
from streamlit.testing.v1 import AppTest

from feedback import enviar_sugestao
from render_seguro import texto, link_https, link_mapa

ENDPOINT = "https://exemplo.invalid/endpoint-ficticio"


class TransporteTest(unittest.TestCase):
    def test_demo_nao_envia_mesmo_com_endpoint_e_transporte_fornecidos(self):
        state = {}
        post = Mock(side_effect=AssertionError("A demo não pode enviar"))
        for endpoint in [ENDPOINT, "https://formspree.io/f/exemplo-ficticio", "http://localhost/test"]:
            self.assertEqual(enviar_sugestao(endpoint, "Sugestão fictícia", state, post=post), "modo_demo")
        post.assert_not_called()
        self.assertEqual(state, {})

    def test_demo_repetida_nao_registra_falso_sucesso(self):
        state = {"preservar": "fixture"}
        for _ in range(2):
            self.assertEqual(enviar_sugestao(ENDPOINT, "Teste fictício", state), "modo_demo")
        self.assertEqual(state, {"preservar": "fixture"})

    def test_mensagem_invalida_nao_envia_nem_altera_estado(self):
        post = Mock()
        state = {}
        for message in ["   ", "x" * 2001, None, 42]:
            self.assertEqual(enviar_sugestao(ENDPOINT, message, state, post=post), "invalida")
        post.assert_not_called()
        self.assertEqual(state, {})


class RenderTest(unittest.TestCase):
    def test_texto_e_links_injetados_nao_viram_html_executavel(self):
        value = "<img src=x onerror=alert(1)>\"'"
        self.assertNotIn("<img", texto(value))
        self.assertIn("&lt;img", texto(value))
        self.assertEqual(link_https("javascript:alert(1)"), "")
        self.assertEqual(link_https("https://user:pass@exemplo.invalid"), "")
        self.assertNotIn("'", link_https("https://exemplo.invalid/' onclick='test"))
        maps = link_mapa("' onmouseover='alert(1)", "A&B")
        self.assertNotIn("'", maps)
        self.assertIn("%26", maps)
        self.assertIn("&amp;", maps)

    def test_config_protecoes_ativas(self):
        config = tomllib.loads(Path(".streamlit/config.toml").read_text(encoding="utf-8"))
        self.assertTrue(config["server"]["enableCORS"])
        self.assertTrue(config["server"]["enableXsrfProtection"])


class InterfaceTest(unittest.TestCase):
    def test_demo_nao_le_planilha_historica_nao_envia_e_filtra(self):
        with patch.dict(os.environ, {"SUGGESTION_ENDPOINT": "https://formspree.io/f/exemplo-ficticio"}), patch("pandas.read_excel", side_effect=AssertionError("Não ler base histórica")), patch("requests.sessions.Session.request", side_effect=AssertionError("Não enviar HTTP")):
            app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "projeto1.py"), default_timeout=30).run()
            self.assertEqual(len(app.exception), 0)
            self.assertEqual(app.metric[0].value, "3")
            app.text_area[0].set_value("Mensagem fictícia")
            app.button[0].click().run()
            self.assertEqual(len(app.exception), 0)
            self.assertTrue(any("Não houve envio externo" in item.value for item in app.info))
            self.assertEqual(len(app.success), 0)
            app.multiselect[0].set_value(["Bairro fictício Sul"]).run()
            self.assertEqual(len(app.exception), 0)
            self.assertEqual(app.metric[0].value, "1")
            app.number_input[0].set_value(3_000_000).run()
            self.assertEqual(app.metric[0].value, "0")
            self.assertIn("Nenhum empreendimento", app.info[-1].value)


if __name__ == "__main__":
    unittest.main()
