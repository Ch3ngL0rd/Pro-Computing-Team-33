import pandas as panda
import sqlite3

def update_database(data):
    try:
            # Connect to the SQLite database 
            connection = sqlite3.connect('DATABASE_NAME.db')  # Replace 'DATABASE_NAME' with name of database 

            # Loop through the DataFrame rows and update the database
            for index, row in data.iterrows():
                # Extract data from the rows
                column1_data = row['COLUMN_1']  # Replace 'COLUMN_1' with the actual column name
                column2_data = row['COLUMN_2']  # Replace 'COLUMN_2' with the actual column name

                # Define the SQL query to update the database
                update_query = f"UPDATE your_table SET column1 = '{column1_data}', column2 = '{column2_data}' WHERE id = {index + 1}"

                # Execute the query
                connection.execute(update_query)

            connection.commit()

    except Exception as error:
        print("An error occurred while updating the database:", error)

    finally:
        connection.close()


def main():
    excel_file_path = 'FILE_NAME.xls' # Replace 'FILE_NAME' with name of excel file 
    excel_data = panda.read_excel(excel_file_path)
    update_database(excel_data)
