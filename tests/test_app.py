import unittest
from app import app

class HoaSmokeTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_health(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "ok")

    def test_dashboard_bootstrap_includes_finance(self):
        response = self.client.get("/api/bootstrap")
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["community"]["name"], "Canyon Ridge HOA")
        self.assertIn("assessments", payload["finance"])
        self.assertIn("invoices", payload["finance"])
        self.assertGreaterEqual(len(payload["finance"]["assessments"]), 1)

    def test_create_work_order_requires_title(self):
        response = self.client.post("/api/work-orders", json={"title": ""})
        self.assertEqual(response.status_code, 400)

if __name__ == "__main__":
    unittest.main()
