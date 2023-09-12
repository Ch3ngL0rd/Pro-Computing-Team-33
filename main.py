from app.gui.TkinterApp import TkinterApp
from app.databases.sqlite_handbookDB import Sqlite_handbookDB
import platform
import subprocess


def main():
    handbook_db = Sqlite_handbookDB()

    handbook_db.populate_sampleDB()

    main_window = TkinterApp()
    main_window.run_tkinter_app()


if __name__ == "__main__":
    main()