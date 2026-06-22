from unittest.mock import patch

from django.test import SimpleTestCase


class HealthCheckTest(SimpleTestCase):
    @patch("project.health_check._check_cache", return_value={"healthy": True})
    @patch("project.health_check._check_redis", return_value={"healthy": True})
    @patch("project.health_check._check_database", return_value={"healthy": True})
    def test_health_endpoint(self, mock_database, mock_redis, mock_cache):
        response = self.client.get("/health/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "healthy")

    @patch("project.health_check._check_cache", return_value={"healthy": True})
    @patch("project.health_check._check_redis", return_value={"healthy": False})
    @patch("project.health_check._check_database", return_value={"healthy": True})
    def test_health_endpoint_returns_503_when_a_check_fails(
        self,
        mock_database,
        mock_redis,
        mock_cache,
    ):
        response = self.client.get("/health/")

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["status"], "degraded")


class ReadinessCheckTest(SimpleTestCase):
    @patch("project.health_check._check_redis", return_value={"healthy": True})
    @patch("project.health_check._check_database", return_value={"healthy": True})
    def test_readiness_endpoint(self, mock_database, mock_redis):
        response = self.client.get("/ready/")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["ready"])


class LivenessCheckTest(SimpleTestCase):
    def test_liveness_endpoint(self):
        response = self.client.get("/live/")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["alive"])
