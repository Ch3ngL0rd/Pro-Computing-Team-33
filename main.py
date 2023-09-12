import file_selector
import calculate
import platform
import subprocess


def main():
    
    try:
        import tkinter as tk  # Python 3.x
    except ImportError:
        os_type = platform.system()
        if os_type == 'Darwin':  # Darwin indicates macOS
            print("You are on macOS. Running the shell command...")
            subprocess.run("/bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"", shell=True) # Replace 'ls' with your desired shell command
            subprocess.run("brew update", shell=True)
            subprocess.run("brew install python", shell=True)
            subprocess.run("brew install python-tk", shell=True)          

        else:
            print(f"You are on {os_type}. The shell command will not be executed.")
        
    selected_file_path = file_selector.open_file()

    if selected_file_path:
        calculate.calculations(selected_file_path)
    else:
        print("No file selected.")

if __name__ == "__main__":
    main()