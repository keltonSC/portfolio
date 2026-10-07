from pathlib import Path
import unittest

from streamlit.testing.v1 import AppTest


class AppTests(unittest.TestCase):
    def test_modes_and_missing_uploads_have_safe_messages(self):
        app = AppTest.from_file(str(Path(__file__).parents[1] / "PDFapp.py"), default_timeout=15).run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(len(app.error), 0)
        self.assertIn("Gerador de PDF", app.title[0].value)
        app.button[0].click().run()
        self.assertEqual(app.error[0].value, "Envie a foto de capa!")
        app.sidebar.radio[0].set_value("Marca d'água em lote").run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(len(app.error), 0)
        self.assertIn("Envie as imagens", app.info[0].value)
        app.sidebar.radio[0].set_value("Folheto + anexar fotos do lote").run()
        app.button[0].click().run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(app.error[0].value, "Envie a foto de capa!")


if __name__ == "__main__":
    unittest.main()
