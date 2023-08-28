"""_summary_
"""

from databases.studentDB import StudentDB

import sqlite3

"""_summary_
"""
class Sqlite_studentDB(StudentDB):
    def __init__(self) -> None:
        self.connection = sqlite3.connect(':memory:')
        self.cursor = self.connection.cursor()


    def create_db(self):
        # Init tables
        self.cursor.execute('''
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

        self.cursor.execute('''
        CREATE TABLE Units (
            unit_code TEXT PRIMARY KEY,
            unit_title TEXT        
        );
        ''')

        self.cursor.execute('''
        CREATE TABLE Enrollments (
            student_id TEXT,
            unit_code TEXT,
            mark INTEGER,

            FOREIGN KEY(student_id) REFERENCES Students(student_id),
            FOREIGN KEY(unit_code) REFERENCES Units(unit_code)
            PRIMARY KEY(student_id, unit_code)        
        );
        ''')


    def init_test_data(self):
        # populate tables created in create_db

        # add student
        self.cursor.execute('''
        INSERT INTO
            Students(student_id, surname, given_name, student_title, course_code, course_title, major_deg)
            VALUES('23001000', 'Alban', 'Robert', 'Mr', 'BH011', 'Bachelor of Engineering (Honours)', 'Mechanical Engineering');
        ''')

        self.cursor.execute('''
        INSERT INTO
            Students(student_id, surname, given_name, student_title, course_code, course_title, major_deg)
            VALUES('23002002', 'Bleaker', 'Mary', 'Miss', 'BH011', 'Bachelor of Engineering (Honours)', 'Mechanical Engineering');
        ''')

        # add units
        self.cursor.execute("INSERT INTO Units(unit_code, unit_title) VALUES('PHYS1001', 'Physics for Scientists and Engineers');")
        self.cursor.execute("INSERT INTO Units(unit_code, unit_title) VALUES('MATH1011', 'Multivariable Calculus');")
        self.cursor.execute("INSERT INTO Units(unit_code, unit_title) VALUES('GENG1010', 'Introduction to Engineering');")

        # add enrollments 
        self.cursor.execute("INSERT INTO Enrollments(student_id, unit_code, mark) VALUES('23001000', 'PHYS1001', 70);")
        self.cursor.execute("INSERT INTO Enrollments(student_id, unit_code, mark) VALUES('23001000', 'MATH1011', 97);")
        self.cursor.execute("INSERT INTO Enrollments(student_id, unit_code, mark) VALUES('23001000', 'GENG1010', 76);")
        self.cursor.execute("INSERT INTO Enrollments(student_id, unit_code, mark) VALUES('23002002', 'GENG1010', 77);")
        self.cursor.execute("INSERT INTO Enrollments(student_id, unit_code, mark) VALUES('23002002', 'PHYS1001', 57);")

    def test_query(self) -> str:
        # print all queries

        
        
        pass


# testing
if __name__ == "__main__":
    student_db = Sqlite_studentDB()

    student_db.create_db()
    student_db.init_test_data()

    print(student_db.query())