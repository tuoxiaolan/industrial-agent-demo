import unittest

from fastapi.testclient import TestClient

from config import API_KEY
from fastapi_app import app


class FastAPITests(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)
        self.headers = {
    "x-api-key": API_KEY,
}

    def test_health(self):
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["ok"])

    def test_parameter_requires_api_key(self):
        response = self.client.get(
            "/parameter",
            params={
                "model": "Device-B",
                "field": "提升电机功率",
            },
        )

        self.assertEqual(response.status_code, 401)

    def test_parameter_success(self):
        response = self.client.get(
            "/parameter",
            params={
                "model": "Device-B",
                "field": "提升电机功率",
            },
            headers=self.headers,
        )

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertTrue(data["ok"])
        self.assertEqual(data["value"], 4.0)
        self.assertEqual(data["unit"], "kW")

    def test_chat_manual_search(self):
        response = self.client.post(
            "/chat",
            json={
                "question": "Device-B的维护流程是什么？",
            },
            headers=self.headers,
        )

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertTrue(data["ok"])
        self.assertEqual(
            data["tool_call"]["name"],
            "search_manual",
        )

    def test_chat_ticket_requires_confirmation(self):
        response = self.client.post(
            "/chat",
            json={
                "question": "给Device-B创建一个提升电机功率异常工单",
            },
            headers=self.headers,
        )

        self.assertEqual(response.status_code, 202)

        data = response.json()

        self.assertTrue(data["requires_confirmation"])
        self.assertEqual(
            data["tool_call"]["name"],
            "create_maintenance_ticket",
        )

    def test_create_and_list_ticket(self):
        create_response = self.client.post(
            "/ticket",
            json={
                "model": "Device-B",
                "issue": "自动测试工单",
                "evidence": "来自test_fastapi.py",
            },
            headers=self.headers,
        )

        self.assertEqual(create_response.status_code, 200)

        ticket = create_response.json()["ticket"]
        self.assertTrue(ticket["ticket_id"].startswith("MT-"))

        list_response = self.client.get(
            "/tickets",
            headers=self.headers,
        )

        self.assertEqual(list_response.status_code, 200)

        tickets = list_response.json()["tickets"]
        ticket_ids = [item["ticket_id"] for item in tickets]

        self.assertIn(ticket["ticket_id"], ticket_ids)


if __name__ == "__main__":
    unittest.main()