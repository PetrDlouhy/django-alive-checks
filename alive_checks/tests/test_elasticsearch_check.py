import json
import socket
from unittest import TestCase, mock

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.test import RequestFactory, override_settings
from django_alive import HealthcheckFailure
from django_alive.views import healthcheck

from alive_checks.checks import check_elasticsearch

if not settings.configured:
    settings.configure()


class ElasticsearchCheckTests(TestCase):

    @mock.patch("alive_checks.checks.elasticsearch.Elasticsearch")
    def test_elasticsearch_ping_success(self, mock_elasticsearch):
        mock_elasticsearch.return_value.ping.return_value = True
        try:
            check_elasticsearch()
        except HealthcheckFailure:
            self.fail("HealthcheckFailure raised unexpectedly")

    @mock.patch("alive_checks.checks.elasticsearch.Elasticsearch")
    def test_elasticsearch_ping_failure(self, mock_elasticsearch):
        mock_elasticsearch.return_value.ping.return_value = False
        with self.assertRaises(HealthcheckFailure):
            check_elasticsearch()

    @mock.patch("alive_checks.checks.elasticsearch.Elasticsearch")
    def test_elasticsearch_exception(self, mock_elasticsearch):
        mock_elasticsearch.side_effect = Exception("Connection failed")
        with self.assertRaises(HealthcheckFailure):
            check_elasticsearch()


class ElasticsearchHealthcheckViewTests(TestCase):
    """django-alive turns only its own HealthcheckFailure into a 503."""

    def get_healthcheck(self, es_settings=None):
        check = ("alive_checks.checks.check_elasticsearch", {"settings": es_settings})
        with override_settings(ALIVE_CHECKS=[check]):
            response = healthcheck(RequestFactory().get("/healthz/"))
        return response.status_code, json.loads(response.content)

    @mock.patch("alive_checks.checks.elasticsearch.Elasticsearch")
    def test_reachable_elasticsearch_is_healthy(self, mock_elasticsearch):
        mock_elasticsearch.return_value.ping.return_value = True
        self.assertEqual(self.get_healthcheck(), (200, {"healthy": True}))

    def test_unreachable_elasticsearch_is_reported_as_503(self):
        with socket.socket() as bound_not_listening:
            bound_not_listening.bind(("127.0.0.1", 0))
            port = bound_not_listening.getsockname()[1]
            with self.assertLogs("alive_checks.checks.elasticsearch", "ERROR"):
                result = self.get_healthcheck({"hosts": [f"http://127.0.0.1:{port}"]})
        self.assertEqual(
            result, (503, {"healthy": False, "errors": ["Elasticsearch error"]})
        )

    @mock.patch("alive_checks.checks.elasticsearch.Elasticsearch")
    def test_client_exception_is_reported_as_503(self, mock_elasticsearch):
        mock_elasticsearch.side_effect = Exception("Connection failed")
        with self.assertLogs("alive_checks.checks.elasticsearch", "ERROR"):
            result = self.get_healthcheck()
        self.assertEqual(
            result, (503, {"healthy": False, "errors": ["Elasticsearch exception"]})
        )
