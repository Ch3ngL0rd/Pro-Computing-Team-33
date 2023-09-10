import file_selector
import calculate

def main():
    selected_file_path = file_selector.open_file()

    if selected_file_path:
        calculate.calculations(selected_file_path)
    else:
        print("No file selected.")

if __name__ == "__main__":
    main()