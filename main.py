from app.gui.TkinterApp import TkinterApp
from app.logic import calculate
import platform
import subprocess


def main():
    main_window = TkinterApp()
    main_window.run_tkinter_app()


if __name__ == "__main__":
    main()