import unittest

# set path to proj path (parent dir)
import sys
import os
current_dir = os.getcwd()
proj_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(proj_dir)

# import 
from src.app.logic.marks_processor import Marks_processor

class TestExcelProcessing(unittest.TestCase):
    def setUp(self) -> None:
        self.marks_processor = Marks_processor()

    # ================================= Valid file testing =================================
    def test_valid_file_xls(self):
        input_file = 'valid_file.xls'
        
        result = self.marks_processor.process_file(input_file)

        # Check that the output file was created
        self.assertTrue(os.path.exists(output_file), "Output file should be created")

    def test_valid_file_xlsx(self):
        input_file = 'valid_file.xlsx'
        
        result = self.marks_processor.process_file(input_file)

        # Check that the output file was created
        self.assertTrue(os.path.exists(output_file), "Output file should be created")

    # ================================= Valid file testing =================================

    # ================================= Invalid file testing =================================

    def test_invalid_file(self):
        input_file = 'invalid_file.csv'

        # Attempt to process the input file, expecting an exception 
        with self.assertRaises(Exception) as context:
            self.marks_processor.process_file(input_file)

        # Define the expected error message
        expected_error_message = "Input file is not an Excel file"

         # Check that the error message matches the expected one
        self.assertIn(expected_error_message, str(context.exception))

    # ================================= Invalid file testing =================================

if __name__ == '__main__':
    unittest.main()
