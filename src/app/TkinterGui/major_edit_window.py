import tkinter as tk
from tkinter import ttk

WINDOW_HEIGHT = 1080
WINDOW_WIDTH = 1920


class Major_edit_window:
    def __init__(self, handbook_db, root):
        self.handbook_db = handbook_db
        # Array of rule_id, x,y,width,height
        # Used to store the position of each rule table for drag and drop
        self.dragging_unit = None  # To keep track of the unit being dragged
        self.tables = []
        self.root = root

    def initialize_UI(self):
        self.handbook_window = tk.Toplevel(self.root)
        self.handbook_window.transient(self.root)
        self.handbook_window.grab_set()
        self.handbook_window.title("Handbook Settings")
        self.handbook_window.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

        notebook = ttk.Notebook(self.handbook_window)
        self.units_frame = ttk.Frame(notebook)
        self.majors_frame = ttk.Frame(notebook)
        self.rules_search_frame = ttk.Frame(notebook)
        notebook.add(self.units_frame, text="Units")
        notebook.add(self.majors_frame, text="Majors")
        notebook.add(self.rules_search_frame, text="Rules")
        notebook.pack(expand=1, fill="both")

        self.initialize_units_tab()
        self.initialize_majors_tab()
        self.initialize_rules_tab()
        self.handbook_window.mainloop()

    def initialize_rules_tab(self):
        frame = tk.Frame(self.rules_search_frame)
        frame.pack(side="top", fill="x", padx=5, pady=10)

        # Create a new frame to hold the ID input and search button
        input_frame = tk.Frame(frame)
        input_frame.pack(side="left", fill="x")

        # Create and place the ID input (text box) within the input_frame
        self.rule_id_entry = tk.Entry(input_frame)
        self.rule_id_entry.pack(side="left", padx=5)

        # Create and place the search button next to the ID input
        search_button = tk.Button(input_frame, text="Search", command=self.on_search_button_clicked)
        search_button.pack(side="left", padx=5)

        # Create a frame to hold the rule tables and put it inside the rules_search_frame
        self.search_rule_frame = tk.Frame(self.rules_search_frame)
        self.search_rule_frame.pack(fill="x", padx=5, pady=10)  # Pack it into the main rules tab frame

    def on_search_button_clicked(self):
        # Get the rule ID from the text box
        rule_id = self.rule_id_entry.get()
        
        # Pass it to your search or refresh function (assuming it's `refresh_searched_rule`)
        self.refresh_searched_rule(rule_id)


    def refresh_searched_rule(self, value):
        # Clear existing rules if any
        for widget in self.search_rule_frame.winfo_children():
            widget.destroy()
        rule_id = self.rule_id_entry.get()
        print(rule_id)
        # Fetch new rules and populate
        rules_data = self.handbook_db.fetch_rule_verbose(rule_id)
        print(rules_data)
        if rules_data == []:
            print("HI")
            self.show_error_message(self.search_rule_frame, rule_id)
        else:
        #Fetch major details
            major_details = self.handbook_db.fetch_rule_major(rule_id)
            year = major_details[1]
            major = major_details[0]
            

            for index, (rule_id, credit_points, units) in enumerate(rules_data):
                self.create_search_rule_table(self.search_rule_frame, rule_id, credit_points, year, major,units, rule_id)

    def show_error_message(self, frame, rule_id):
        rule_frame = tk.Frame(frame)
        header_frame = tk.Frame(rule_frame)
        header_frame.pack(fill="x")

        tk.Label(header_frame, text=f"No rule found with ID {rule_id}", font=("Arial", 16)).pack(side="left")


        rule_frame.pack(fill="x", padx=10, pady=5)
        self.handbook_window.update_idletasks()
        
        
    def create_search_rule_table(self, frame, rule_name, credit_points,yr,major,units, rule_id):
        rule_frame = tk.Frame(frame)
        header_frame = tk.Frame(rule_frame)
        header_frame.pack(fill="x")

        tk.Label(header_frame, text=f"{rule_name} From {major}, {yr} - Credit Points: {credit_points}", font=("Arial", 16)).pack(side="left")

        # Create the main Treeview for displaying units
        tree = ttk.Treeview(rule_frame, columns=("Unit Name", "Unit Credit Points"), show="headings")
        tree.heading("#1", text="Unit Name")
        tree.heading("#2", text="Unit Credit Points")

        for unit in units:
            unit_name, unit_credit_points = unit
            tree.insert("", "end", values=(unit_name, unit_credit_points))

        tree.pack(fill="both", expand=True)  # Ensure the treeview is packed and visible

        rule_frame.pack(fill="x", padx=10, pady=5)
        self.handbook_window.update_idletasks()


    def initialize_majors_tab(self):
        top_frame = tk.Frame(self.majors_frame)
        top_frame.pack(side="top", fill="x", padx=5, pady=10)

        # Create a new frame to hold the year and major dropdowns
        dropdown_frame = tk.Frame(top_frame)
        dropdown_frame.pack(side="left", fill="x")

        # check case when there are no year_options
        year_options = self.handbook_db.fetch_years()


        # Create and place the Year dropdown within the dropdown_frame
        self.year_var = tk.StringVar()
        self.year_var.set("Select Year")

        if year_options:
            self.year_menu = tk.OptionMenu(
                dropdown_frame, self.year_var, *year_options, command=self.update_major_dropdown)
        else:
            self.year_menu = tk.OptionMenu(dropdown_frame, self.year_var, "Select Year")
            self.year_menu.configure(state="disabled")

        self.year_menu.pack(side="left", anchor="n")

        # Create and place the Major dropdown within the dropdown_frame (initially empty and hidden)
        self.major_var = tk.StringVar()
        self.major_var.set("Select Major")
        self.major_menu = tk.OptionMenu(dropdown_frame, self.major_var, "")
        self.major_menu.pack(side="left", anchor="n")
        self.major_menu.pack_forget()  # Hide the major dropdown initially

        # Add a trace to major_var to update rules when it changes
        self.major_var.trace_add("write", self.refresh_rules_section)

        # Create and place the "Add Major" button
        tk.Button(top_frame, text="Add Major", command=self.show_add_major_dialog).pack(
            side="right", anchor="n")
        
        # Create and place the "Delete Major" button
        tk.Button(top_frame, text="Delete Major", command=self.delete_major).pack(
            side='right', anchor="n", padx=5)

        # Create and place the "Add Rule" button
        tk.Button(top_frame, text="Add Rule", command=self.show_add_rule_dialog).pack(
            side='right', anchor="n", padx=5)


        # Create a frame to hold the All Units section and the Rules Table section
        self.handbook_window.bind("<ButtonRelease-1>", self.end_drag)

        # Initialize the All Units section (Left 1/3)
        self.initialize_all_units_section()

        # Initialize the Rules Table section (Right 2/3)
        self.initialize_rules_section()

    def refresh_majors_tab(self, *args):
        # Clear existing rules if any
        for widget in self.majors_frame.winfo_children():
            widget.destroy()

        # Reinitialize the majors tab
        self.initialize_majors_tab()

    def show_add_rule_dialog(self):
        dialog = tk.Toplevel(self.handbook_window)
        dialog.transient(self.handbook_window)
        dialog.grab_set()

        tk.Label(dialog, text="Credit Points:").grid(row=0, column=0, padx=10, pady=10)

        credit_points_entry = tk.Entry(dialog)
        credit_points_entry.grid(row=0, column=1, padx=10, pady=10)

        def add_rule():
            try:
                credit_points = int(credit_points_entry.get())
            except ValueError:
                # Handle non-integer input, you can show an error dialog or a message
                print("Please enter a valid integer for credit points.")
                return

            # Add the rule and get its ID
            rule_id = self.handbook_db.create_rule_and_get_id(credit_points)
            
            # Link the rule to the current selected major
            major_id = self.handbook_db.get_major_id(self.major_var.get(), self.year_var.get())  # Assuming you have a method to get major_id based on major name and year
            self.handbook_db.link_major_rule(major_id, rule_id)

            
            dialog.destroy()
            self.refresh_rules_section()

        tk.Button(dialog, text="OK", command=add_rule).grid(row=1, columnspan=2, padx=10, pady=10)

    def initialize_all_units_section(self):
        # Create a frame for the "All Units" section
        all_units_frame = tk.Frame(self.majors_frame, width=200)
        all_units_frame.pack(side="left", fill="both", padx=5, pady=5)

        # Create and place a search bar at the top of the frame
        search_entry = tk.Entry(all_units_frame)
        search_entry.insert(0, "Search for a unit")
        search_entry.bind(
            "<FocusIn>", lambda event: self.clear_placeholder(event, search_entry))
        search_entry.bind(
            "<FocusOut>", lambda event: self.add_placeholder(event, search_entry))
        search_entry.bind("<KeyRelease>", self.update_search_major)
        search_entry.pack(side="top", fill="x", padx=5, pady=5)

        # Create a Treeview to display all units
        self.all_units_tree = ttk.Treeview(all_units_frame, columns=(
            "Unit Code", "Credit Points"), show="headings")

        self.unit_selection = ""
        self.all_units_tree.heading("#1", text="Unit Code")
        self.all_units_tree.heading("#2", text="Credit Points")
        
                # Create the Delete Treeview for delete actions
        self.unit_select_tree = ttk.Treeview(all_units_frame, columns=("Actions"), show="headings")
        self.unit_select_tree.heading("#1", text="Actions")

        self.unit_select_tree.bind("<ButtonRelease-1>", self.select_unit)

        self.unit_select_tree.pack(fill = "both",side="right")
        
        
        self.all_units_tree.pack(fill = "both", side="left")
        self.all_units_tree.bind("<ButtonPress-1>", self.start_drag)

        # Populate the Treeview
        self.populate_all_units()
        
    def select_unit(self, event):
        item = self.unit_select_tree.selection()[0]
        values = self.all_units_tree.item(item, 'values')
        self.unit_selection = values[0]
        print(self.unit_selection)
        
    def populate_all_units(self):
        for unit in self.handbook_db.fetch_all_units_with_credit():
            self.all_units_tree.insert("", "end", values=unit)
            self.unit_select_tree.insert("", "end", values=("Select",))

    def update_search_major(self, event):
        search_term = event.widget.get().lower()
        # Clear current tree view
        self.all_units_tree.delete(*self.all_units_tree.get_children())
        for unit in self.handbook_db.fetch_all_units_with_credit():
            unit_name, credit_points = unit
            if search_term in unit_name.lower():
                self.all_units_tree.insert(
                    "", "end", values=(unit_name, credit_points))
                
    def refresh_major_units(self):
        self.all_units_tree.delete(*self.all_units_tree.get_children())
        self.populate_all_units()

    def initialize_rules_section(self):
        # Create a canvas and a vertical scrollbar and link them
        canvas = tk.Canvas(self.majors_frame,highlightthickness=0)
        scrollbar = tk.Scrollbar(
            self.majors_frame, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        # Create a frame to hold the rule tables and put it inside the canvas
        self.rules_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=self.rules_frame, anchor="nw")

        self.rules_frame.bind("<Configure>", lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")))

        # Now add the canvas and scrollbar to the GUI
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def refresh_rules_section(self, *args):
        # Clear existing rules if any
        for widget in self.rules_frame.winfo_children():
            widget.destroy()

        # Fetch new rules and populate
        rules_data = self.handbook_db.fetch_major_rules_verbose(
            major=self.major_var.get(),
            year=self.year_var.get()
        )

        print(rules_data)

        for index, (rule_id, credit_points, units) in enumerate(rules_data):
            self.create_rule_table(self.rules_frame, index+1, credit_points, units,rule_id)


    def create_rule_table(self, frame, rule_name, credit_points, units, rule_id):
        def add_unit():
            if(self.unit_selection != ""):
                self.add_unit_to_rule(rule_id, self.unit_selection)
                self.unit_selection = ""
        
        def delete_rule():
            print(f"Deleting {rule_name}")
            self.handbook_db.delete_rule( rule_id)
            self.refresh_rules_section()

        def delete_unit(unit_name, rule_id):
            print(f"Deleting {unit_name} from {rule_name}")
            self.handbook_db.unlink_unit_rule(unit_name, rule_id)
            self.refresh_rules_section()

        def on_delete_tree_select(event):
            item = delete_tree.selection()[0]
            values = tree.item(item, 'values')
            unit_name = values[0]
            delete_unit(unit_name, rule_id)

        rule_frame = tk.Frame(frame)
        header_frame = tk.Frame(rule_frame)
        header_frame.pack(fill="x")

        tk.Label(header_frame, text=f"{rule_name} - Credit Points: {credit_points}", font=("Arial", 16)).pack(side="left")
        tk.Button(header_frame, text="Delete Rule", command=delete_rule).pack(side="right")
        tk.Button(header_frame, text="Add Unit", command=add_unit).pack(side="right")

        # Create the main Treeview for displaying units
        tree = ttk.Treeview(rule_frame, columns=("Unit Code", "Unit Credit Points"), show="headings")
        tree.heading("#1", text="Unit Code")
        tree.heading("#2", text="Unit Credit Points")

        # Create the Delete Treeview for delete actions
        delete_tree = ttk.Treeview(rule_frame, columns=("Actions"), show="headings")
        delete_tree.heading("#1", text="Actions")

        for unit in units:
            unit_name, unit_credit_points = unit
            tree.insert("", "end", values=(unit_name, unit_credit_points))
            delete_tree.insert("", "end", values=("Delete",))

        delete_tree.bind("<ButtonRelease-1>", on_delete_tree_select)

        tree.pack(side="left", fill="x")
        delete_tree.pack(side="right", fill="x")

        rule_frame.pack(fill="x", padx=10, pady=5)
        self.handbook_window.update_idletasks()

        x, y, width, height = rule_frame.winfo_x(), rule_frame.winfo_y(), rule_frame.winfo_width(), rule_frame.winfo_height()
        self.tables.append((rule_id, x, y, width, height))
    def start_drag(self, event):
        try:
            selected_item = self.all_units_tree.selection()[0]  # Get selected item
            self.dragging_unit = self.all_units_tree.item(selected_item, 'values')
            print("Dragging:", self.dragging_unit)
        except IndexError:
            pass
    
    def end_drag(self, event):
        None

    def find_target_rule(self, x, y):
        for rule_id, rule_x, rule_y, width, height in self.tables:
            if rule_x <= x <= rule_x + width and rule_y <= y <= rule_y + height:
                return rule_id
        return None
    
    def add_unit_to_rule(self, rule_id, unit):
        # Your code to add the unit to the rule goes here
        if unit is None:
            return
        print(f"Adding {unit} to {rule_id}")  # Debugging print statement
        self.handbook_db.link_unit_rule(unit, rule_id)
        self.refresh_rules_section()
    def update_major_dropdown(self, selected_year): 
        # Update the Major dropdown based on the selected year
        # Fetch majors for the selected year from the database
        self.major_var.set("Select Major")
        majors_for_year = self.handbook_db.fetch_majors_for_year(selected_year)

        # Clear the current options in the major dropdown
        self.major_menu["menu"].delete(0, "end")

        # Sort alphabetically
        majors_for_year.sort()

        # Populate the major dropdown with new options
        for major in majors_for_year:
            self.major_menu["menu"].add_command(
                label=major, command=tk._setit(self.major_var, major))

        self.major_menu.pack()  # Show the major dropdown
        
    def update_major_dropdown_dup(self, selected_year):
        # Update the Major dropdown based on the selected year
        # Fetch majors for the selected year from the database
        self.major_var.set("Select Major")
        majors_for_year = self.handbook_db.fetch_majors_for_year(selected_year)

        # Clear the current options in the major dropdown
        self.major_menu_dup["menu"].delete(0, "end")

        # Populate the major dropdown with new options
        for major in majors_for_year:
            self.major_menu_dup["menu"].add_command(
                label=major, command=tk._setit(self.major_var_dup, major))

    def show_add_major_dialog(self):
        dialog = tk.Toplevel(self.handbook_window)
        dialog.transient(self.handbook_window)
        dialog.grab_set()

        tk.Label(dialog, text="Major Name:").grid(row=0, column=0)
        tk.Label(dialog, text="Year:").grid(row=1, column=0)
        
        major_name_entry = tk.Entry(dialog)
        year_entry = tk.Entry(dialog)

        major_name_entry.grid(row=0, column=1)
        year_entry.grid(row=1, column=1)

        # Adding the heading above dropdowns
        tk.Label(dialog, text="Create Based on an Existing Major").grid(row=2, column=0, columnspan=2)

        year_options = self.handbook_db.fetch_years()

        # Create and place the Year dropdown
        self.year_var_dup = tk.StringVar()
        self.year_var_dup.set("Select Year")

        if year_options:
            self.year_menu_dup = tk.OptionMenu(
                dialog, self.year_var_dup, *year_options, command=self.update_major_dropdown_dup)
        else:
            self.year_menu_dup = tk.OptionMenu(dialog, self.year_var_dup, "Select Year")
            self.year_menu_dup.configure(state="disabled")

        self.year_menu_dup.grid(row=3, column=0, columnspan=2)

        # Create and place the Major dropdown (initially empty)
        self.major_var_dup = tk.StringVar()
        self.major_var_dup.set("Select Major")
        self.major_menu_dup = tk.OptionMenu(dialog, self.major_var_dup, "")

        self.major_menu_dup.grid(row=4, column=0, columnspan=2)
        def add_major():
            major_name = major_name_entry.get()
            year = year_entry.get()
            print(self.major_var_dup.get())
            print(self.year_var_dup.get())
            if self.major_var_dup.get() == "Select Major" or self.year_var_dup.get() == "Select Year":
                # Add code here to insert the new major into the database
                self.handbook_db.create_major(major_name, year)
            else:
                print("HIHI")
                self.handbook_db.duplicate_major(self.major_var_dup.get(), int(self.year_var_dup.get()), major_name, int(year))
                print(self.handbook_db.fetch_major_rules_verbose(major_name, int(year)))
            
            dialog.destroy()
            self.refresh_majors_tab()

        tk.Button(dialog, text="OK", command=add_major).grid(
            row=5, columnspan=2)

    # Units Functionality
    def delete_major(self):
        selected_major = self.major_var.get()
        if selected_major != "Select Major":
            major_id = self.handbook_db.get_major_id(selected_major, self.year_var.get())
            self.handbook_db.delete_major(major_id)
            self.refresh_majors_tab()
            self.refresh_unit_section()
        else:
            print("No Major selected to delete.")

    
    def initialize_units_tab(self):
        
        def delete_unit_tree(unit_name):
            print(f"Deleting {unit_name}")
            self.handbook_db.delete_unit(unit_name)
            self.refresh_unit_section()
            self.refresh_major_units()
            self.refresh_rules_section()
        
        def on_delete_tree_select(event):
            item = self.unit_delete_tree.selection()[0]
            values = self.tree.item(item, 'values')
            unit_name = values[0]
            delete_unit_tree(unit_name)
        
        
        # Create a frame to hold the search bar and button
        top_frame = tk.Frame(self.units_frame)
        top_frame.pack(fill='x')

        # Create a search bar with placeholder
        search_bar = tk.Entry(top_frame, width=40)
        search_bar.insert(0, "Search for a unit")
        search_bar.bind(
            '<FocusIn>', lambda event: self.clear_placeholder(event, search_bar))
        search_bar.bind(
            '<FocusOut>', lambda event: self.add_placeholder(event, search_bar))
        search_bar.bind('<KeyRelease>', self.update_search)
        # Pack to the left side of the frame
        search_bar.pack(side='left', pady=10)

        # Create New Unit Button
        tk.Button(top_frame, text="Create New Unit", command=self.show_add_unit_dialog).pack(
            side='right', pady=10)  # Pack to the right side of the frame

        # Create Treeview with height set to 10 rows
        self.tree = ttk.Treeview(self.units_frame, columns=(
            "Unit Code", "Credit Points"), show="headings", height=10)
        self.tree.heading("#1", text="Unit Code")
        self.tree.heading("#2", text="Credit Points")
        
        self.unit_delete_tree = ttk.Treeview(self.units_frame, columns=("Actions"), show="headings")
        self.unit_delete_tree.heading("#1", text="Actions")
        
        self.unit_delete_tree.bind("<ButtonRelease-1>", on_delete_tree_select)

        #delete_tree.bind("<ButtonRelease-1>", on_delete_tree_select)

        #tree.pack(side="left", fill="x")
        self.tree.pack(side = "left", fill='both',  expand = True)
        self.unit_delete_tree.pack(side="left", fill="both",)
        
        


        self.populate_units()

    def clear_placeholder(self, event, entry):
        if entry.get() == "Search for a unit":
            entry.delete(0, tk.END)

    def add_placeholder(self, event, entry):
        if not entry.get():
            entry.insert(0, "Search for a unit")

    def update_search(self, event):
        search_term = event.widget.get().lower()
        self.tree.delete(*self.tree.get_children())
        for unit in self.handbook_db.fetch_all_units_with_credit():
            unit_name, credit_points = unit
            if search_term in unit_name.lower():
                self.tree.insert("", "end", values=(unit_name, credit_points))

    def populate_units(self):
        for unit in self.handbook_db.fetch_all_units_with_credit():
            self.tree.insert("", "end", values=unit)
            self.unit_delete_tree.insert("", "end", values="Delete")
    
    def refresh_unit_section(self, *args):
        # Clear existing rules if any
        for widget in self.units_frame.winfo_children():
            widget.destroy()
            
        self.initialize_units_tab()
        self.refresh_rules_section()
        
    def show_add_unit_dialog(self):
        dialog = tk.Toplevel(self.handbook_window)
        dialog.transient(self.handbook_window)
        dialog.grab_set()

        tk.Label(dialog, text="Unit Code:").grid(
            row=0, column=0, padx=10, pady=10)
        tk.Label(dialog, text="Credit Points:").grid(
            row=1, column=0, padx=10, pady=10)

        unit_name_entry = tk.Entry(dialog)
        credit_points_entry = tk.Entry(dialog)

        unit_name_entry.grid(row=0, column=1, padx=10, pady=10)
        credit_points_entry.grid(row=1, column=1, padx=10, pady=10)

        def add_unit():
            unit_name = unit_name_entry.get()
            credit_points = credit_points_entry.get()
            self.tree.insert("", "end", values=(unit_name, credit_points))
            self.handbook_db.create_unit(unit_name, credit_points)
            self.refresh_major_units()
            dialog.destroy()

        tk.Button(dialog, text="OK", command=add_unit).grid(
            row=2, columnspan=2, padx=10, pady=10)
        self.handbook_window.wait_window(dialog)
