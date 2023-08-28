from databases.studentDB import StudentDB

import sqlite3


class Sqlite_studentDB(StudentDB):
    def create_db(self):
        connection = sqlite3.connect(':memory:')
        cursor = connection.cursor()


        cursor.execute('''
            CREATE TABLE Students
        ''')

        cursor.execute('''
            CREATE TABLE Unit
        ''')

        print("student database created")
