import unittest

import time

# get path to import file reader implementation
import sys
import os
# Get the current working directory
current_directory = os.getcwd()

# Go up two directories
proj_dir = os.path.abspath(os.path.join(current_directory, "..", ".."))
print(proj_dir)
sys.path.append(proj_dir)

from file_processing.excel_file_reader import Excel_file_reader
from databases.sqlite_studentDB import Sqlite_studentDB

class File_reader_Tests(unittest.TestCase):
    def test_timed(self):

        start_time = time.time()

        print("initialising db and reader")
        file_path = r'../test_files/Example Data BE(Hons).xlsx'

        file_reader = Excel_file_reader()
        student_db = Sqlite_studentDB()
        student_db.create_db()

        print("--- %s seconds ---" % (time.time() - start_time))

        print("extracting data")
        file_data = file_reader.extract_data(file_path)
        print("--- %s seconds ---" % (time.time() - start_time))

        print("storing data")
        file_reader.store_data(file_data, student_db)
        print("--- %s seconds ---" % (time.time() - start_time))

        print("quering data")
        result = student_db._execute("SELECT * FROM Students;")
        for i in result:
            print(i)
        
        print("--- %s seconds ---" % (time.time() - start_time))
