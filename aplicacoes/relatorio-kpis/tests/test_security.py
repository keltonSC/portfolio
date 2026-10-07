import os
from pathlib import Path
import time
import unittest
from unittest.mock import Mock, patch

import requests

from security import CRMError, authorized, crm_json, live_enabled, require_authorized_user


class Stop(RuntimeError):
    pass


class AccessTests(unittest.TestCase):
    def setUp(self):
        self.claims = {"is_logged_in": True, "email_verified": True, "email": "person@example.invalid", "exp": 2000}
        self.allowlist = ["person@example.invalid"]

    def test_verified_exact_identity_allowed_until_expiry(self):
        self.assertTrue(authorized(self.claims, self.allowlist, now=1000))
        self.assertFalse(authorized(self.claims, self.allowlist, now=2000))

    def test_unverified_anonymous_and_other_identity_denied(self):
        for changes in ({"is_logged_in": False}, {"email_verified": False}, {"email_verified": "true"}, {"email": "other@example.invalid"}):
            self.assertFalse(authorized(self.claims | changes, self.allowlist, now=1000))

    def test_empty_allowlist_and_invalid_expiry_denied(self):
        self.assertFalse(authorized(self.claims, [], now=1000))
        self.assertFalse(authorized(self.claims, "person@example.invalid", now=1000))
        for expiry in (None, "2000", True, float("nan"), float("inf")):
            self.assertFalse(authorized(self.claims | {"exp": expiry}, self.allowlist, now=1000))

    def test_email_matching_never_grants_a_domain_or_suffix(self):
        self.assertFalse(authorized(self.claims | {"email": "person@example.invalid.evil.test"}, self.allowlist, now=1000))

    def test_live_mode_requires_explicit_true(self):
        for value in ("", "false", "TRUE", "1"):
            with patch.dict(os.environ, {"RELATORIO_LIVE_ENABLED": value}):
                self.assertFalse(live_enabled())

    def test_gate_denies_before_reading_service_secrets(self):
        st = Mock()
        st.session_state = {"cv_df_leads": "private", "inter_df": "private", "__leads_diag__": {"broker_samples": "private"}, "public_preference": True}
        st.stop.side_effect = Stop
        with patch.dict(os.environ, {"RELATORIO_LIVE_ENABLED": "false"}):
            with self.assertRaises(Stop):
                require_authorized_user(st)
        self.assertEqual(st.session_state, {"public_preference": True})
        st.secrets.get.assert_not_called()

    def test_unauthorized_gate_clears_data_and_stops(self):
        st = Mock()
        st.session_state = {"cv_df_leads": "private", "_authorized_identity": "old@example.invalid"}
        st.secrets = {"access": {"allowed_emails": []}}
        st.user = self.claims
        st.button.return_value = False
        st.stop.side_effect = Stop
        with patch.dict(os.environ, {"RELATORIO_LIVE_ENABLED": "true"}):
            with self.assertRaises(Stop):
                require_authorized_user(st)
        self.assertEqual(st.session_state, {})

    def test_authorized_identity_change_removes_previous_private_data(self):
        st = Mock()
        st.session_state = {"cv_df_leads": "old fixture", "__leads_diag__": "old fixture", "_authorized_identity": "old@example.invalid", "public_preference": True}
        st.secrets = {"access": {"allowed_emails": self.allowlist}}
        st.user = self.claims | {"exp": time.time() + 60}
        st.sidebar.button.return_value = False
        with patch.dict(os.environ, {"RELATORIO_LIVE_ENABLED": "true"}):
            require_authorized_user(st)
        self.assertEqual(st.session_state, {"_authorized_identity": "person@example.invalid", "public_preference": True})

    def test_logout_clears_private_data_before_leaving(self):
        st = Mock()
        st.session_state = {"cv_df_leads": "fixture", "__leads_diag__": "fixture", "_authorized_identity": "person@example.invalid"}
        st.secrets = {"access": {"allowed_emails": self.allowlist}}
        st.user = self.claims | {"exp": time.time() + 60}
        st.sidebar.button.return_value = True
        st.stop.side_effect = Stop
        with patch.dict(os.environ, {"RELATORIO_LIVE_ENABLED": "true"}):
            with self.assertRaises(Stop):
                require_authorized_user(st)
        self.assertEqual(st.session_state, {})
        st.logout.assert_called_once()


class TransportTests(unittest.TestCase):
    def request(self, session, **kwargs):
        args = dict(subdomain="demo", path="/api/cvio/lead", email="service@example.invalid", token="fixture-only", params={"limit": 20, "offset": 0})
        return crm_json(session, **(args | kwargs))

    def test_secrets_in_headers_only_with_timeout_and_no_redirects(self):
        session = Mock()
        session.get.return_value.status_code = 200
        session.get.return_value.json.return_value = {"data": []}
        self.assertEqual(self.request(session), (200, {"data": []}))
        url = session.get.call_args.args[0]
        config = session.get.call_args.kwargs
        self.assertNotIn("fixture-only", url)
        self.assertEqual(config["params"], {"limit": 20, "offset": 0})
        self.assertEqual(config["headers"]["token"], "fixture-only")
        self.assertEqual(config["timeout"], (5, 30))
        self.assertIs(config["allow_redirects"], False)

    def test_errors_and_redirects_do_not_retry_or_expose_body(self):
        for status in (301, 401, 403, 429, 500):
            session = Mock()
            session.get.return_value.status_code = status
            session.get.return_value.text = "sensitive-body"
            with self.assertRaises(CRMError) as caught:
                self.request(session)
            self.assertNotIn("sensitive-body", str(caught.exception))
            session.get.assert_called_once()
            session.get.return_value.json.assert_not_called()

    def test_invalid_json_does_not_fallback_to_query_credentials(self):
        session = Mock()
        session.get.return_value.status_code = 200
        session.get.return_value.json.side_effect = ValueError("sensitive-body")
        with self.assertRaises(CRMError) as caught:
            self.request(session)
        self.assertNotIn("sensitive-body", str(caught.exception))
        session.get.assert_called_once()

    def test_network_exception_is_sanitized(self):
        session = Mock()
        session.get.side_effect = requests.ConnectionError("url?token=sensitive-fixture")
        with self.assertRaises(CRMError) as caught:
            self.request(session)
        self.assertNotIn("sensitive-fixture", str(caught.exception))

    def test_subdomain_and_path_cannot_select_another_host(self):
        session = Mock()
        for changes in ({"subdomain": "demo@evil.test"}, {"subdomain": "demo.evil.test"}, {"subdomain": "demo/evil"}, {"path": "/other"}):
            with self.assertRaises(CRMError):
                self.request(session, **changes)
        session.get.assert_not_called()

    def test_query_secrets_and_excessive_limits_rejected(self):
        session = Mock()
        for params in ({"token": "fixture-only"}, {"limit": 5001}, {"pagina": 1001}, {"offset": -1}, {"limit": True}):
            with self.assertRaises(CRMError):
                self.request(session, params=params)
        session.get.assert_not_called()


class UIIntegrationTests(unittest.TestCase):
    def test_public_default_starts_with_fixtures_and_no_http(self):
        from streamlit.testing.v1 import AppTest
        with patch.dict(os.environ, {"RELATORIO_LIVE_ENABLED": "false"}), patch.object(requests.Session, "get", side_effect=AssertionError("No external network in demo")):
            app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "streamlit_app.py"))
            app.session_state["cv_df_leads"] = "old private fixture"
            app.session_state["__leads_diag__"] = "old private fixture"
            app.run(timeout=20)
            self.assertEqual(len(app.exception), 0)
            self.assertNotIn("cv_df_leads", app.session_state)
            self.assertNotIn("__leads_diag__", app.session_state)
            self.assertEqual([m.value for m in app.metric], ["120", "36", "12"])
            app.selectbox[0].select("Outubro fictício").run()
            self.assertEqual([m.value for m in app.metric], ["150", "45", "15"])

    def test_live_without_identity_never_loads_crm(self):
        from streamlit.testing.v1 import AppTest
        with patch.dict(os.environ, {"RELATORIO_LIVE_ENABLED": "true"}), patch.object(requests.Session, "get", side_effect=AssertionError("Unauthorized network call")):
            app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "streamlit_app.py")).run(timeout=20)
            self.assertEqual(len(app.exception), 0)
            self.assertGreater(len(app.warning), 0)
            self.assertEqual(len(app.metric), 0)


if __name__ == "__main__":
    unittest.main()
