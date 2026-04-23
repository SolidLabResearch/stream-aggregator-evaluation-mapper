import unittest
from mapper.core import annotate_event, generate_uuid, map_value, update_source_id

class TestCore(unittest.TestCase):
    def test_generate_uuid(self):
        # Reset uuid_map implicitly by using a unique patient_id or just checking increment
        id1 = generate_uuid("metric1", "patient1")
        id2 = generate_uuid("metric1", "patient1")
        self.assertEqual(id2, id1 + 1)

    def test_update_source_id(self):
        # wearable.acceleration.x -> Accelerometer
        self.assertEqual(update_source_id("sensor1", "wearable.acceleration.x"), "sensor1.Accelerometer")
        # Unknown metric -> same source_id
        self.assertEqual(update_source_id("sensor1", "unknown.metric"), "sensor1")

    def test_map_value_float(self):
        val_str, group = map_value(25.5, "environment.temperature")
        self.assertEqual(group, "CONTEXT")
        self.assertIn("25.5", val_str)
        self.assertIn("float", val_str)

    def test_map_value_bool(self):
        val_str, group = map_value(1, "environment.motion")
        self.assertEqual(group, "CONTEXT")
        self.assertIn("\"1\"", val_str)
        self.assertIn("integer", val_str)

    def test_annotate_event_valid(self):
        event = {
            "sourceId": "participant1.sensor1",
            "metricId": "environment.temperature",
            "value": 22.5,
            "timestamp": "2023-10-27T10:00:00.000Z"
        }
        result = annotate_event(event)
        self.assertIsNotNone(result)
        self.assertIn("participant1", result)
        self.assertIn("sensor1", result)
        self.assertIn("22.5", result)
        self.assertIn("2023-10-27T10:00:00.000Z", result)

    def test_annotate_event_invalid(self):
        event = {"sourceId": "p1"} # Missing fields
        result = annotate_event(event)
        self.assertIsNone(result)

if __name__ == "__main__":
    unittest.main()
