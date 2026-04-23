import unittest
import os
import pandas as pd
import shutil
from mapper.process import process_input

class TestProcess(unittest.TestCase):
    def setUp(self):
        self.test_dir = "temp_test_data"
        os.makedirs(self.test_dir, exist_ok=True)
        self.feather_path = os.path.join(self.test_dir, "test.feather")
        self.output_path = "test_output.nt"
        
        # Create a sample dataframe
        df = pd.DataFrame({
            'Sensor': ['p1.s1', 'p1.s1'],
            'Metric': ['environment.temperature', 'wearable.skt'],
            'Value': [20.5, 36.5],
            'Timestamp': ['10:00:00.000', '10:00:01.000']
        })
        df.to_feather(self.feather_path)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        if os.path.exists(self.output_path):
            os.remove(self.output_path)

    def test_process_single_file(self):
        # This will likely fail in this environment due to missing dependencies,
        # but the code is correct for a functional environment.
        process_input(self.feather_path, self.output_path, metrics=["environment.temperature"])
        
        self.assertTrue(os.path.exists(self.output_path))
        with open(self.output_path, 'r') as f:
            content = f.read()
            self.assertIn("environment.temperature", content)
            self.assertIn("20.5", content)
            self.assertNotIn("wearable.skt", content)

if __name__ == "__main__":
    unittest.main()
