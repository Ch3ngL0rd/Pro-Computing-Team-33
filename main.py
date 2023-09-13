from app.TkinterGui.main_window import Main_window
from app.databases.sqlite_handbookDB import Sqlite_handbookDB
# from app.logic.calculate import calculations
import platform
import subprocess


def main():
    handbook_db = Sqlite_handbookDB()

    # init calculation object and parse handbook db

    handbook_db.populate_sampleDB()

    main_window = Main_window()
    main_window.draw_window()


if __name__ == "__main__":
    main()