from databases.studentDB import StudentDB

import sqlite3


class Sqlite_studentDB(StudentDB):
    def create_db(self):
        conn = sqlite3.connect(':memory:')
        cursor = conn.cursor()

        
        cursor.execute('''
            CREATE TABLE 
        ''')

        print("student database created")
