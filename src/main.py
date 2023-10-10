from app.TkinterGui.main_window import Main_window
from app.databases.sqlite_handbookDB import Sqlite_handbookDB
from app.logic.marks_processor import Marks_processor

import os


# Get the directory where the main.py file is located
current_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(current_dir)

handbook_db_file = 'handbook.db'
handbook_db_path = os.path.join(current_dir, handbook_db_file)
handbook_db = Sqlite_handbookDB(handbook_db_path)


def main():
    marks_processor = Marks_processor(handbookDB=handbook_db)

    # marks_processor.process_file(input_filepath='../Example Data BE(Hons).xlsx',output_filepath='../Example Data BE(Hons)_output.xlsx')

    main_window = Main_window(marks_processor=marks_processor, handbook_db=handbook_db)
    main_window.draw_window()


if __name__ == "__main__":
    try:
        main()
    finally:
        handbook_db.db_commit()