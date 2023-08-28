"""_summary_
"""

from studentDB import StudentDB

import sqlite3

"""_summary_
"""
class Sqlite_studentDB(StudentDB):
    def __init__(self) -> None:
        self.connection = sqlite3.connect(':memory:')


    def create_db(self):
        cursor = self.connection.cursor()

        # Init tables
        cursor.execute('''
        CREATE TABLE Students (
            student_id TEXT PRIMARY KEY,
            surname TEXT,
            given_name TEXT,
            student_title TEXT,
            course_code TEXT,
            course_title TEXT,
            major_deg TEXT            
        );
        ''')

        cursor.execute('''
        CREATE TABLE Units (
            unit_code TEXT PRIMARY KEY,
            unit_title TEXT        
        );
        ''')

        cursor.execute('''
        CREATE TABLE Enrollments (
            student_id TEXT,
            unit_code TEXT,
            mark INTEGER,

            FOREIGN KEY(student_id) REFERENCES Students(student_id),
            FOREIGN KEY(unit_code) REFERENCES Units(unit_code)
            PRIMARY KEY(student_id, unit_code)        
        );
        ''')

        cursor.close()


    """
    executes queries on database
    """
    def _execute(self, query: str) -> list:
        cursor = self.connection.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        return result



# testing
if __name__ == "__main__":
    pass