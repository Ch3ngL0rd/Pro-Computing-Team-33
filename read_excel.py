import pandas as panda
import sqlite3

def update_database(excel_data):
    try:
        # Connect to the SQLite database 
        connection = sqlite3.connect('sqlite_studentDB.py')  

        # Loop through the DataFrame rows and update the database
        for index, row in excel_data.iterrows():
            # Extract data from the rows
            column1_data = row['Person_ID'] 
            column2_data = row['Surname']  
            column3_data = row['Given Names']
            column4_data = row['Student_Title']
            column5_data = row['Course_Code']
            column6_data = row['Course_Title']
            column7_data = row['Major_Deg']
            column8_data = row['Unit_Code']
            column9_data = row['Unit_Title']
            column10_data = row['YEAR']
            column11_data = row['Teaching_Period']
            column12_data = row['Enrolled_Credit_Points']
            column13_data = row['Achievable_Credit_Points']
            column14_data = row['Grade']
            column15_data = row['Mark']
            
            update_query = (
                "UPDATE your_table\n"
                f"SET column1 = {column1_data},\n"
                f"column2 = {column2_data},\n"  
                f"column3 = {column3_data},\n"
                f"column4 = {column4_data},\n"
                f"column5 ={column5_data},\n"
                f"column6 = {column6_data},\n"
                f"column7 = {column7_data},\n"
                f"column8 = {column8_data},\n"
                f"column9 = {column9_data},\n"
                f"column10 = {column10_data},\n"
                f"column11 = {column11_data},\n"
                f"column12 = {column12_data},\n"
                f"column13 = {column13_data},\n"
                f"column14 = {column14_data},\n"
                f"column15 = {column15_data},\n"
                f"WHERE id = {index + 1}"
            )

            # Execute the query
            connection.execute(update_query)

            connection.commit()

    except Exception as error:
        print("An error occurred while updating the database:", error)

    finally:
        connection.close()


def main():
    excel_file_name = 'FILE_NAME.xls' # Replace 'FILE_NAME' with name of excel file 
    excel_data = panda.read_excel(excel_file_name)
    update_database(excel_data)

if __name__ == "__main__":
    main()
