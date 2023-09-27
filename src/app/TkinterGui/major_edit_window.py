import tkinter as tk
from tkinter import ttk

WINDOW_HEIGHT = 1080
WINDOW_WIDTH = 1920


class Major_edit_window:
    def __init__(self, handbook_db):
        self.handbook_db = handbook_db
        # Array of rule_id, x,y,width,height
        # Used to store the position of each rule table for drag and drop
        self.dragging_unit = None  # To keep track of the unit being dragged
        self.tables = []

    def initialize_UI(self):
        self.root = tk.Tk()
        self.root.title("Settings")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

        notebook = ttk.Notebook(self.root)
        self.units_frame = ttk.Frame(notebook)
        self.majors_frame = ttk.Frame(notebook)
        notebook.add(self.units_frame, text="Units")
        notebook.add(self.majors_frame, text="Majors")
        notebook.pack(expand=1, fill="both")

        self.initialize_units_tab()
        self.initialize_majors_tab()
        self.root.mainloop()

    def initialize_majors_tab(self):
        top_frame = tk.Frame(self.majors_frame)
        top_frame.pack(side="top", fill="x", padx=5, pady=10)

        # Create a new frame to hold the year and major dropdowns
        dropdown_frame = tk.Frame(top_frame)
        dropdown_frame.pack(side="left", fill="x")

        year_options = self.handbook_db.fetch_years(self.cursor)

        # Create and place the Year dropdown within the dropdown_frame
        self.year_var = tk.StringVar()
        self.year_var.set("Select Year")
        self.year_menu = tk.OptionMenu(
            dropdown_frame, self.year_var, *year_options, command=self.update_major_dropdown)
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

        # Create a frame to hold the All Units section and the Rules Table section
        self.root.bind("<ButtonRelease-1>", self.end_drag)

        # Initialize the All Units section (Left 1/3)
        self.initialize_all_units_section()

        # Initialize the Rules Table section (Right 2/3)
        self.initialize_rules_section()

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
            "Unit Name", "Credit Points"), show="headings")


        self.all_units_tree.heading("#1", text="Unit Name")
        self.all_units_tree.heading("#2", text="Credit Points")
        self.all_units_tree.pack(fill="both", expand=True, padx=5, pady=5)
        self.all_units_tree.bind("<ButtonPress-1>", self.start_drag)

        # Populate the Treeview
        self.populate_all_units()

    def populate_all_units(self):
        for unit in self.handbook_db.fetch_all_units_with_credit(self.cursor):
            self.all_units_tree.insert("", "end", values=unit)

    def update_search_major(self, event):
        search_term = event.widget.get().lower()
        # Clear current tree view
        self.all_units_tree.delete(*self.all_units_tree.get_children())
        for unit in self.handbook_db.fetch_all_units_with_credit(self.cursor):
            unit_name, credit_points = unit
            if search_term in unit_name.lower():
                self.all_units_tree.insert(
                    "", "end", values=(unit_name, credit_points))

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
            cursor=self.cursor,
            major=self.major_var.get(),
            year=self.year_var.get()
        )


        for index, (rule_id, credit_points, units) in enumerate(rules_data):
            self.create_rule_table(self.rules_frame, index+1, credit_points, units,rule_id)


    def create_rule_table(self, frame, rule_name, credit_points, units, rule_id):
        def delete_rule():
            print(f"Deleting {rule_name}")
            self.handbook_db.delete_rule(self.cursor, rule_id)
            self.refresh_rules_section()

        def delete_unit(unit_name, rule_id):
            print(f"Deleting {unit_name} from {rule_name}")
            self.handbook_db.unlink_unit_rule(self.cursor, unit_name, rule_id)
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

        # Create the main Treeview for displaying units
        tree = ttk.Treeview(rule_frame, columns=("Unit Name", "Unit Credit Points"), show="headings")
        tree.heading("#1", text="Unit Name")
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
        self.root.update_idletasks()

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
        x, y = event.x, event.y
        print("Dropped at:", x, y)
        target_rule = self.find_target_rule(x, y)
        if target_rule:
            self.add_unit_to_rule(target_rule, self.dragging_unit)
        self.dragging_unit = None

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
        self.handbook_db.link_unit_rule(self.cursor, unit[0], rule_id)
        self.refresh_rules_section()
    def update_major_dropdown(self, selected_year):
        # Update the Major dropdown based on the selected year
        # Fetch majors for the selected year from the database
        self.major_var.set("Select Major")
        majors_for_year = self.handbook_db.fetch_majors_for_year(
            self.cursor, selected_year)

        # Clear the current options in the major dropdown
        self.major_menu["menu"].delete(0, "end")

        # Populate the major dropdown with new options
        for major in majors_for_year:
            self.major_menu["menu"].add_command(
                label=major, command=tk._setit(self.major_var, major))

        self.major_menu.pack()  # Show the major dropdown

    def show_add_major_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(dialog, text="Major Name:").grid(row=0, column=0)
        tk.Label(dialog, text="Year:").grid(row=1, column=0)

        major_name_entry = tk.Entry(dialog)
        year_entry = tk.Entry(dialog)

        major_name_entry.grid(row=0, column=1)
        year_entry.grid(row=1, column=1)

        def add_major():
            major_name = major_name_entry.get()
            year = year_entry.get()
            # Add code here to insert the new major into the database
            self.handbook_db.create_major(self.cursor, major_name, year)
            dialog.destroy()

        tk.Button(dialog, text="OK", command=add_major).grid(
            row=2, columnspan=2)

    # Units Functionality
    

    
    def initialize_units_tab(self):
        
        def delete_unit_tree(unit_name):
            print(f"Deleting {unit_name}")
            self.handbook_db.delete_unit(self.cursor, unit_name)
            self.refresh_unit_section()
        
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
            "Unit Name", "Credit Points"), show="headings", height=10)
        self.tree.heading("#1", text="Unit Name")
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
        for unit in self.handbook_db.fetch_all_units_with_credit(self.cursor):
            unit_name, credit_points = unit
            if search_term in unit_name.lower():
                self.tree.insert("", "end", values=(unit_name, credit_points))

    def populate_units(self):
        for unit in self.handbook_db.fetch_all_units_with_credit(self.cursor):
            self.tree.insert("", "end", values=unit)
            self.unit_delete_tree.insert("", "end", values="Delete")
    
    def refresh_unit_section(self, *args):
        # Clear existing rules if any
        for widget in self.units_frame.winfo_children():
            widget.destroy()
            
        self.initialize_units_tab()
        self.refresh_rules_section()
        
    def show_add_unit_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(dialog, text="Unit Name:").grid(
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
            self.handbook_db.create_unit(self.cursor, unit_name, credit_points)
            dialog.destroy()

        tk.Button(dialog, text="OK", command=add_unit).grid(
            row=2, columnspan=2, padx=10, pady=10)
        self.root.wait_window(dialog)
