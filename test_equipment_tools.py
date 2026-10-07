import unittest

from equipment_tools import (
    create_maintenance_ticket,
    get_equipment_parameter,
)


class EquipmentParameterTests(unittest.TestCase):

    def test_create_ticket(self):
        result = create_maintenance_ticket(
            "Device-B",
            "提升电机功率异常",
            "设备重量1500 kg，提升电机功率应为4.0 kW",
        )

        self.assertTrue(result["ok"])
        self.assertEqual(result["ticket"]["model"], "Device-B")
        self.assertEqual(result["ticket"]["status"], "created")
        self.assertTrue(result["ticket"]["ticket_id"].startswith("MT-"))

    def test_device_a_power(self):
        result = get_equipment_parameter("Device-A", "提升电机功率")

        self.assertTrue(result["ok"])
        self.assertEqual(result["value"], 3.0)
        self.assertEqual(result["unit"], "kW")

    def test_device_a_weight(self):
        result = get_equipment_parameter("Device-A", "设备重量")

        self.assertTrue(result["ok"])
        self.assertEqual(result["value"], 1200)
        self.assertEqual(result["unit"], "kg")

    def test_device_b_power(self):
        result = get_equipment_parameter("Device-B", "提升电机功率")

        self.assertTrue(result["ok"])
        self.assertEqual(result["value"], 4.0)
        self.assertEqual(result["unit"], "kW")

    def test_alias(self):
        result = get_equipment_parameter("Device-B", "处理能力")

        self.assertTrue(result["ok"])
        self.assertEqual(result["field"], "整粒生产能力")
        self.assertEqual(result["value"], "100～1000")
        self.assertEqual(result["unit"], "kg/h")

    def test_weight_is_not_capacity(self):
        result = get_equipment_parameter("Device-B", "设备重量")

        self.assertTrue(result["ok"])
        self.assertEqual(result["value"], 1500)
        self.assertEqual(result["unit"], "kg")

    def test_unknown_field(self):
        result = get_equipment_parameter("Device-B", "最大负载")

        self.assertFalse(result["ok"])


if __name__ == "__main__":
    unittest.main()