"""
This file initialises the program
initialises db files
and opens UI
"""
from databases.sqlite_studentDB import Sqlite_studentDB
from file_processing.excel_file_reader import Excel_file_reader


def main():
    # init file path for test data
    file_path = r'./test_files/Example Data BE(Hons).xlsx'

    # initialises required databases
    student_db = Sqlite_studentDB()
    student_db.create_db()

    # initialise file reader
    file_reader = Excel_file_reader()

    # read file
    file_data = file_reader.extract_data(file_path)

    # store data to student db
    file_reader.store_data(file_data, student_db)

    # query data in db
    print("quering data")
    result = student_db._execute("SELECT * FROM Students;")
    for i in result:
        print(i)



if __name__ == "__main__":
    main()