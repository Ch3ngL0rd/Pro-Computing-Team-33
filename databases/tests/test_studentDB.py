from ..sqlite_studentDB import Sqlite_studentDB

import unittest


class StudentDB_Tests(unittest.TestCase):
    def init_db(self):
        self.student_db = Sqlite_studentDB()
        self.student_db.create_db()

        # populate tables created in create_db
        # add student
        self.student_db._execute('''
        INSERT INTO
            Students(student_id, surname, given_name, student_title, course_code, course_title, major_deg)
            VALUES('23001000', 'Alban', 'Robert', 'Mr', 'BH011', 'Bachelor of Engineering (Honours)', 'Mechanical Engineering');
        ''')

        self.student_db._execute('''
        INSERT INTO
            Students(student_id, surname, given_name, student_title, course_code, course_title, major_deg)
            VALUES('23002002', 'Bleaker', 'Mary', 'Miss', 'BH011', 'Bachelor of Engineering (Honours)', 'Mechanical Engineering');
        ''')

        # add units
        self.student_db._execute("INSERT INTO Units(unit_code, unit_title) VALUES('PHYS1001', 'Physics for Scientists and Engineers');")
        self.student_db._execute("INSERT INTO Units(unit_code, unit_title) VALUES('MATH1011', 'Multivariable Calculus');")
        self.student_db._execute("INSERT INTO Units(unit_code, unit_title) VALUES('GENG1010', 'Introduction to Engineering');")

        # add enrollments 
        self.student_db._execute("INSERT INTO Enrollments(student_id, unit_code, mark) VALUES('23001000', 'PHYS1001', 70);")
        self.student_db._execute("INSERT INTO Enrollments(student_id, unit_code, mark) VALUES('23001000', 'MATH1011', 97);")
        self.student_db._execute("INSERT INTO Enrollments(student_id, unit_code, mark) VALUES('23001000', 'GENG1010', 76);")
        self.student_db._execute("INSERT INTO Enrollments(student_id, unit_code, mark) VALUES('23002002', 'GENG1010', 77);")
        self.student_db._execute("INSERT INTO Enrollments(student_id, unit_code, mark) VALUES('23002002', 'PHYS1001', 57);")


    def test_queries(self):
        # print all enrollments
        results = self.student_db._execute("SELECT * FROM Enrollments;")
        enrollments = "\n".join(results)
        expected_enrollments = "('23001000', 'PHYS1001', 70)\n('23001000', 'MATH1011', 97)\n('23001000', 'GENG1010', 76)\n('23002002', 'GENG1010', 77)\n('23002002', 'PHYS1001', 57)"
        self.assertEqual(enrollments, expected_enrollments)


        # # print enerollments for a single student
        # output = self.student_db._execute("SELECT * FROM Enrollments WHERE student_id = '23002002';")

        # # print students that do the same unit
        # output = self.student_db._execute('''
        #     SELECT Students.student_id, Students.surname, Students.given_name
        #     FROM Students
        #     INNER JOIN Enrollments ON Students.student_id = Enrollments.student_id
        #     WHERE Enrollments.unit_code = 'PHYS1001';
        # ''')
