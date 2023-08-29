import unittest

# get path to immport db implementation
import sys
import os
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from sqlite_studentDB import Sqlite_studentDB

class StudentDB_Tests(unittest.TestCase):
    def test_db(self):
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


        ## test sample data
        # print all enrollments
        enrollments = self.student_db._execute("SELECT * FROM Enrollments;")    
        self.assertEqual(len(enrollments), 5)
        self.assertEqual(enrollments[0], ('23001000', 'PHYS1001', 70))
        self.assertEqual(enrollments[1], ('23001000', 'MATH1011', 97))
        self.assertEqual(enrollments[2], ('23001000', 'GENG1010', 76))
        self.assertEqual(enrollments[3], ('23002002', 'GENG1010', 77))
        self.assertEqual(enrollments[4], ('23002002', 'PHYS1001', 57))

        # print enerollments for a single student
        enrollments = self.student_db._execute("SELECT * FROM Enrollments WHERE student_id = '23002002';")
        self.assertEqual(len(enrollments), 2)
        self.assertEqual(enrollments[0], ('23002002', 'GENG1010', 77))
        self.assertEqual(enrollments[1], ('23002002', 'PHYS1001', 57))

        # print students that do the same unit
        students = self.student_db._execute('''
            SELECT Students.student_id, Students.surname, Students.given_name
            FROM Students
            INNER JOIN Enrollments ON Students.student_id = Enrollments.student_id
            WHERE Enrollments.unit_code = 'PHYS1001';
        ''')
        self.assertEqual(len(students), 2)
        self.assertEqual(students[0], ('23001000', 'Alban', 'Robert'))
        self.assertEqual(students[1], ('23002002', 'Bleaker', 'Mary'))


    def test_add_student(self):
        self.student_db = Sqlite_studentDB()
        self.student_db.create_db()

        # test that the student has been added properly
        student_1 = {
            'student_id': '23001000',
            'surname': 'Alban',
            'given_name': 'Robert',
            'student_title': 'Mr.',
            'course_code': 'BH011',
            'course_title': 'Bachelor of Engineering (Honours)',
            'major_deg': 'Mechanical Engineering'
        }

        self.student_db.add_student(student_1)
        students = self.student_db._execute('''
            SELECT Students.student_id, Students.surname, Students.given_name FROM Students
        ''')
        self.assertEqual(students[0], ('23001000', 'Alban', 'Robert'))


        # test the case where a duplicate student record is added

        # test the case where a student changes degree

        # test the case where a student changes major
        pass


if __name__ == "__main__":
    unittest.main
