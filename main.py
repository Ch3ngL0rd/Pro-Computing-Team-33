"""
This file initialises the program
initialises db files
and opens UI
"""
from databases.sqlite_studentDB import Sqlite_studentDB

"""_summary_
"""
def main():
    # initialises required databases
    student_db = Sqlite_studentDB()

    student_db.test()

if __name__ == "__main__":
    main()