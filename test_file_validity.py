import unittest
import marksprocessor
import os

class TestExcelProcessing(unittest.TestCase):

    # ================================= Valid file testing =================================
    def test_valid_file_xls(self):
        input_file = 'valid_file.xls'
        
        result = marksprocessor.process_excel(input_file)

        # Check that the output file was created
        self.assertTrue(os.path.exists(output_file), "Output file should be created")

    def test_valid_file_xlsx(self):
        input_file = 'valid_file.xlsx'
        
        result = marksprocessor.process_excel(input_file)

        # Check that the output file was created
        self.assertTrue(os.path.exists(output_file), "Output file should be created")

    # ================================= Valid file testing =================================

    # ================================= Invalid file testing =================================

    def test_invalid_file(self):
        input_file = 'invalid_file.csv'

        # Attempt to process the input file, expecting an exception 
        with self.assertRaises(Exception) as context:
            marksprocessor.process_excel(input_file)

        # Define the expected error message
        expected_error_message = "Input file is not an Excel file"

         # Check that the error message matches the expected one
        self.assertIn(expected_error_message, str(context.exception))

    # ================================= Invalid file testing =================================

if __name__ == '__main__':
    unittest.main()
