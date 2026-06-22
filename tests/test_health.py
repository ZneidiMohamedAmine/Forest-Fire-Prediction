from unittest.mock import patch

from django.test import SimpleTestCase


class HealthCheckTest(SimpleTestCase):
    @patch("project.health_check._check_cache", return_value={"healthy": True})
    @patch("project.health_check._check_redis", return_value={"healthy": True})
    @patch("project.health_check._check_database", return_value={"healthy": True})
    def test_health_endpoint(self, mock_database, mock_redis, mock_cache):
        response = self.client.get("/health/")
        self.assertEqual(response.status_code, 200)
