import pandas as pd

from file_processing.file_reader import File_reader
from databases.studentDB import StudentDB

class Excel_file_reader(File_reader):
    """_summary_

    Args:
        File_reader (_type_): _description_
    """
    def __init__(self) -> None:

        # may be better to have this as a param in constructor
        self.excel_col_names = {
            'student_id': 'Person_ID',
            'surname': 'Surname',
            'given_name': 'Given Names',
            'student_title': 'Student_Title',
            'course_code': 'Course_Code',
            'course_title': 'Course_Title',
            'major_deg': 'Major_Deg',
            'unit_code': 'Unit_Code',
            'unit_title': 'Unit_Title',
            'year': 'YEAR',
            'teaching_period': 'Teaching_Period',
            'enrolled_credit': 'Enrolled_Credit_Points',
            'achievable_credit': 'Achievable_Credit_Points',
            'grade': 'Grade',
            'mark': 'Mark'
        }


    def extract_data(self, file_path: str) -> pd.DataFrame:
        excel_data = pd.read_excel(file_path, engine='openpyxl')
        return excel_data



    def store_data(self, file_data: pd.DataFrame, student_db: StudentDB) -> None:
        # need to add tables for other relationships - majors, courses
        # update tables with data i wasnt storing before, grades, teaching period, year etc
        for _, row in file_data.iterrows():
            student_id = row[self.excel_col_names['student_id']] 
            surname = row[self.excel_col_names['surname']]  
            given_name = row[self.excel_col_names['given_name']]
            student_title = row[self.excel_col_names['student_title']]
            course_code = row[self.excel_col_names['course_code']]
            course_title = row[self.excel_col_names['course_title']]
            major_deg = row[self.excel_col_names['major_deg']]
            unit_code = row[self.excel_col_names['unit_code']]
            unit_title = row[self.excel_col_names['unit_title']]
            year = row[self.excel_col_names['year']]
            teaching_period = row[self.excel_col_names['teaching_period']]
            enrolled_credit = row[self.excel_col_names['enrolled_credit']]
            achievable_credit = row[self.excel_col_names['achievable_credit']]
            grade = row[self.excel_col_names['grade']]
            mark = row[self.excel_col_names['mark']]

            student_data = {
                'student_id': student_id,
                'surname': surname,
                'given_name': given_name,
                'student_title': student_title,
                'course_code': course_code,
                'course_title': course_title,
                'major_deg': major_deg
            }

            unit_data = {
                'unit_code': unit_code,
                'unit_title': unit_title
            }

            enrollment_data = {
                'student_id': student_id,
                'unit_code': unit_code,
                'mark': mark
            }

            student_db.add_student(student_data)
            # student_db.add_unit(unit_data)
            # student_db.add_enrollment(enrollment_data)
