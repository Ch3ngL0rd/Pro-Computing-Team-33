import sqlite3

class Sqlite_handbookDB():
    def __init__(self, handbook_db_path) -> None:
        """
        Constructor of the Sqlite_handbookDB class.
        
        Connects to the SQLite database located at `handbook_db_path` 
        and initializes the connection object.
        
        Parameters:
        - handbook_db_path (str): Path to the SQLite database file.
        """
        self.conn = sqlite3.connect(handbook_db_path)

    def db_commit(self):
        """
        Commits any pending transaction to the database and closes the connection.
        
        If an error occurs during the commit, an error message is printed.
        """
        try:
            self.conn.commit()
            self.conn.close()
            print("Changes committed to the database.")
        except Exception as e:
            print(f"Error committing changes: {e}")

    def duplicate_major(self, src_major, src_yr, nw_major, nw_yr):
        """
        Duplicates a major from a specified year to a new major and year.
        
        Parameters:
        - src_major (str): Name of the source major.
        - src_yr (int): Year of the source major.
        - nw_major (str): Name of the new major.
        - nw_yr (int): Year of the new major.
        """
        cursor_major = self.create_major(nw_major, nw_yr)
        nw_major_id = cursor_major.lastrowid
        cursor_major.close()

        # Get a list of all rules for the current major
        rules_to_create = self.fetch_major_rules(src_major, src_yr)

        # Iterate through every rule that needs to be created
        for rule in rules_to_create:
            cursor_rule = self.create_rule(rule[1])
            new_rule_id = cursor_rule.lastrowid
            cursor_rule.close()
            self.link_major_rule(nw_major_id, new_rule_id)

            # Get all units to link
            units_to_link = self.fetch_unit_rules(rule[0])
            for unit in units_to_link:
                self.link_unit_rule(unit, new_rule_id)

    def select_all_rules(self, major, yr):
        """
        Retrieves all rules and associated unit codes for a specified major and year.
        
        Parameters:
        - major (str): Name of the major.
        - yr (int): Year of the major.
        
        Returns:
        - output (list of tuple): List containing tuples of (rule_value, [unit_codes]).
        """
        # Gets cursor for conn
        cursor = self.conn.cursor()

        # Query to retrieve the rule values and lists of units for each rule from the db according to provided major & year
        query = """
            SELECT r.VALUE, GROUP_CONCAT(u.UNIT_CODE)
            FROM Rules r
            INNER JOIN MajorRules rm ON r.rule_id = rm.rule_id
            INNER JOIN RuleUnits ur ON r.rule_id = ur.rule_id
            INNER JOIN Units u ON ur.unit_code = u.unit_code
            INNER JOIN Major m ON rm.major_id = m.major_ID
            WHERE m.name = ? AND m.year = ?
            GROUP BY r.rule_id
        """

        # Execute the query with parameters
        cursor.execute(query, (major, yr))

        # Fetch all the results
        results = cursor.fetchall()

        # Process the results and prepare the output
        output = []
        for row in results:
            # Extract values from row
            rule_value, unit_codes = row
            # Split the comma-separated unit codes
            unit_codes_list = unit_codes.split(',')
            # Append to output list
            output.append((rule_value, unit_codes_list))

        return output

    def select_all_major_units(self, major, yr):
        """
        Retrieves all distinct unit codes associated with a specified major and year.
        
        Parameters:
        - major (str): Name of the major.
        - yr (int): Year of the major.
        
        Returns:
        - output (list): List of unit codes.
        """
        # Gets cursor for conn
        cursor = self.conn.cursor()

        # Query to retrieve the rule values and lists of units for each rule from the db according to provided major & year
        query = """
            SELECT distinct u.unit_code
            FROM Rules r
            INNER JOIN MajorRules rm ON r.rule_id = rm.rule_id
            INNER JOIN RuleUnits ur ON r.rule_id = ur.rule_id
            INNER JOIN Units u ON ur.unit_code = u.unit_code
            INNER JOIN Major m ON rm.major_id = m.major_ID
            WHERE m.name = ? AND m.year = ?
        """

        # Execute the query with parameters
        cursor.execute(query, (major, yr))

        # Fetch all the results
        results = cursor.fetchall()
        print(results)

        # Process the results and prepare the output
        output = [row[0] for row in results]

        return output

    def create_unit(self, unit_code, credit_pts):
        """
        Creates a new unit in the database, or provides warnings if the unit already exists.
        
        Parameters:
        - unit_code (str): Code for the new unit.
        - credit_pts (int): Credit points for the new unit.
        """
        cursor = self.conn.cursor()

        # Checks if there is already a unit with the same unit code
        cursor.execute("SELECT * FROM Units WHERE unit_code = ?", (unit_code,))
        results = cursor.fetchall()

        # If there is already a unit with the same unit code, do nothing
        if len(results) > 0:
            # If they have different credit points, print a warning in red
            if results[0][1] != credit_pts:
                print(
                    f"\033[91mWarning: Unit {unit_code} already exists in the database with different credit points\033[0m")

            print(f"Unit {unit_code} already exists in the database")
            return

        # Creates a new unit in the major database based off of provided code/credit pts
        cursor.execute(
            "INSERT INTO Units(unit_code, credit_pts) VALUES(?, ?)", (unit_code, credit_pts))

    def create_rule(self, rule_value):
        """
        Inserts a new rule into the database and returns the cursor.
        
        Parameters:
        - rule_value (int): The value of the new rule.
        
        Returns:
        - cursor (sqlite3.Cursor): The cursor object after insertion.
        """
        cursor = self.conn.cursor()

        cursor.execute("INSERT INTO Rules(value) VALUES(?)", (rule_value,))

        return cursor

    def create_rule_and_get_id(self, rule_value):
        """
        Creates a new rule in the database, commits the transaction, 
        and returns the ID of the new rule.
        
        Parameters:
        - rule_value (int): The value of the new rule.
        
        Returns:
        - rule_id (int): ID of the newly created rule.
        """
        cursor = self.conn.cursor()

        # Insert the new rule
        cursor.execute("INSERT INTO Rules(value) VALUES(?)", (rule_value,))
        self.conn.commit()  # Commit the transaction

        # Get the ID of the last inserted rule
        rule_id = cursor.lastrowid

        return rule_id

    def link_unit_rule(self, unit_code, rule_id):
        """
        Links a unit to a rule in the database.

        Parameters:
            unit_code (str): The code of the unit to be linked.
            rule_id (int): The ID of the rule to which the unit will be linked.

        This function does not return any value.
        """
        cursor = self.conn.cursor()

        cursor.execute(
            "INSERT INTO RuleUnits(unit_code, rule_id) VALUES(?, ?)", (unit_code, rule_id))

    def create_major(self, major_name, major_year):
        """
        Creates a new major in the database.

        Parameters:
            major_name (str): The name of the major to be created.
            major_year (int): The year of the major to be created.

        Returns:
            cursor: A cursor object associated with the database connection.
        """
        cursor = self.conn.cursor()

        cursor.execute("INSERT INTO Major(name, year) VALUES(?,?)",
                       (major_name, major_year))

        return cursor

    def create_major_and_get_id(self, major_name, major_year):
        """
        Creates a new major in the database and retrieves its ID.

        Parameters:
            major_name (str): The name of the major to be created.
            major_year (int): The year of the major to be created.

        Returns:
            int: The ID of the newly created major.
        """

        cursor = self.conn.cursor()

        # Insert the new major
        cursor.execute("INSERT INTO Major(name, year) VALUES(?,?)",
                       (major_name, major_year))

        self.conn.commit()

        # Get the ID of the last inserted major
        major_id = cursor.lastrowid
        return major_id

    def link_major_rule(self, major_id, rule_id):
        """
        Links a major to a rule in the database.

        Parameters:
            major_id (int): The ID of the major to be linked.
            rule_id (int): The ID of the rule to which the major will be linked.

        This function does not return any value.
        """
        cursor = self.conn.cursor()

        cursor.execute(
            "INSERT INTO MajorRules(major_id, rule_id) VALUES(?,?)", (major_id, rule_id))

    def unlink_unit_rule(self, unit_code, rule_id):
        """
        Unlinks a unit from a rule in the database.

        Parameters:
            unit_code (str): The code of the unit to be unlinked.
            rule_id (int): The ID of the rule from which the unit will be unlinked.

        This function does not return any value.
        """
        cursor = self.conn.cursor()

        cursor.execute(
            "DELETE FROM RuleUnits where unit_code = ? AND rule_id = ?", (unit_code, rule_id))

    def unlink_major_rule(self, name, yr, rule_id):
        """
        Unlinks a rule from a major in the database.

        Parameters:
            name (str): The name of the major to be unlinked.
            yr (int): The year of the major to be unlinked.
            rule_id (int): The ID of the rule from which the major will be unlinked.

        This function does not return any value.
        """
        cursor = self.conn.cursor()

        cursor.execute(
            "SELECT major_id from Major where name = ? and year = ?", (name, yr))
        results = cursor.fetchall()
        major_id = results[0][0]

        cursor.execute(
            "DELETE FROM MajorRules where major_id = ? AND rule_id = ?", (major_id, rule_id))

    def delete_unit(self, unit_code):
        """
        Deletes a unit from the database.

        Parameters:
            unit_code (str): The code of the unit to be deleted.

        This function does not return any value.
        """
        cursor = self.conn.cursor()

        cursor.execute("DELETE FROM units where unit_code=?", (unit_code,))

    def delete_major(self, major_id):
        """
        Deletes a major from the database.

        Parameters:
            major_id (int): The ID of the major to be deleted.

        This function does not return any value.
        """
        cursor = self.conn.cursor()
        
        cursor.execute("DELETE FROM Major WHERE major_id=?", (major_id,))

        # deletes rules as well
        cursor.execute("DELETE FROM MajorRules WHERE major_id=?", (major_id,))

    def fetch_all_units(self):
        """
        Fetches all units from the database.

        Returns:
            list: A list of all units in the database.
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT unit_code FROM units")
        rows = cursor.fetchall()
        results = [row[0] for row in rows]
        return results

    def fetch_all_units_with_credit(self):
        """
        Fetch all units along with their credit points from the database.
        
        Returns:
            list: A list of tuples containing the unit code and credit points for all units.
        """
        cursor = self.conn.cursor()

        cursor.execute("SELECT unit_code, credit_pts FROM units")
        rows = cursor.fetchall()
        results = [row for row in rows]
        return results

    def fetch_major_rules(self, major, year):
        """
        Fetch all rules associated with a particular major and year from the database.
        
        Parameters:
            major (str): The name of the major.
            year (int): The year of the major.

        Returns:
            list: A list of tuples containing rule details.
        """

        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT r.*
            FROM Rules r
            INNER JOIN MajorRules rm ON r.rule_id = rm.rule_id
            INNER JOIN Major m ON rm.major_id = m.major_ID
            WHERE m.name = ? AND m.year = ?
            """, (major, year))

        rows = cursor.fetchall()
        results = [row for row in rows]
        return results

    def fetch_major_rules_verbose_by_id(self, major_id):
        """
        Fetch the rules for a major using its ID, including unit codes and credit points for each unit.
        
        Parameters:
            major_id (int): The ID of the major.
            
        Returns:
            list: A list containing rule details along with unit codes and credit points for each unit.
        """

        cursor = self.conn.cursor()
        """ Fetches the rules for a major using its ID, including the unit codes for each rule and credit points for each unit"""
        cursor.execute("""
            SELECT r.*, GROUP_CONCAT(u.UNIT_CODE), GROUP_CONCAT(u.CREDIT_PTS)
            FROM Rules r
            INNER JOIN MajorRules rm ON r.rule_id = rm.rule_id
            INNER JOIN RuleUnits ur ON r.rule_id = ur.rule_id
            INNER JOIN Units u ON ur.unit_code = u.unit_code
            INNER JOIN Major m ON rm.major_id = m.major_ID
            WHERE m.major_id = ?
            GROUP BY r.rule_id
            """, (major_id,))
        rows = cursor.fetchall()
        results = []
        for row in rows:
            rule_id = row[0]
            credit_points = row[1]
            unit_names = row[2].split(',')
            unit_credits = list(map(int, row[3].split(',')))

            # Zip unit_names and unit_credits into a list of tuples
            unit_list = list(zip(unit_names, unit_credits))

            # Create the final dictionary for each rule
            results.append((rule_id, credit_points, unit_list))

        return results
    
    def fetch_rule_major(self, rule_id):
        """
        Fetch the name and year of a major associated with a given rule ID.

        Parameters:
            rule_id (int): The ID of the rule.

        Returns:
            tuple: A tuple containing the name and year of the associated major.
        """

        cursor = self.conn.cursor()
        cursor.execute("""SELECT m.name, m.year
                       FROM Rules r
                       INNER JOIN MajorRules rm on r.rule_id = rm.rule_id
                       INNER JOIN Major m on rm.major_id = m.major_ID
                       WHERE r.rule_id = ?""", (rule_id,))
        
        rows = cursor.fetchall()
        return (rows[0][0], rows[0][1])
        
    def fetch_rule_verbose(self, rule_id):
        """
        Fetch detailed information about a rule based on its ID, including unit codes and credit points.

        Parameters:
            rule_id (int): The ID of the rule.
            
        Returns:
            list: A list containing rule details along with associated unit codes and credit points.
        """

        cursor = self.conn.cursor()
        """ Fetches the rules for a major using its ID, including the unit codes for each rule and credit points for each unit"""
        cursor.execute("""
            SELECT r.*, GROUP_CONCAT(u.UNIT_CODE), GROUP_CONCAT(u.CREDIT_PTS)
            FROM Rules r
            INNER JOIN RuleUnits ur ON r.rule_id = ur.rule_id
            INNER JOIN Units u ON ur.unit_code = u.unit_code
            WHERE r.rule_id = ?
            GROUP BY r.rule_id
            """, (rule_id,))
        rows = cursor.fetchall()
        results = []
        for row in rows:
            rule_id = row[0]
            credit_points = row[1]
            unit_names = row[2].split(',')
            unit_credits = list(map(int, row[3].split(',')))

            # Zip unit_names and unit_credits into a list of tuples
            unit_list = list(zip(unit_names, unit_credits))

            # Create the final dictionary for each rule
            results.append((rule_id, credit_points, unit_list))

        return results

    def delete_rule(self, rule_id):
        """
        Delete a rule from the database using its ID.
        
        Parameters:
            rule_id (int): The ID of the rule to be deleted.
        """

        cursor = self.conn.cursor()

        cursor.execute("DELETE FROM Rules where rule_id = ?", (rule_id,))

    def fetch_years(self):
        """
        Fetch distinct years available in the Major table.
        
        Returns:
            list: A list of distinct years.
        """

        cursor = self.conn.cursor()

        cursor.execute("SELECT DISTINCT year from Major")
        rows = cursor.fetchall()
        results = [row[0] for row in rows]
        return results

    def fetch_majors_for_year(self, year):
        """
        Fetch all major names associated with a given year.
        
        Parameters:
            year (int): The year for which to fetch the majors.
        
        Returns:
            list: A list of major names.
        """

        cursor = self.conn.cursor()

        cursor.execute("SELECT name from Major where year = ?", (year,))
        rows = cursor.fetchall()
        results = [row[0] for row in rows]
        return results

    def fetch_major_rules_verbose(self, major, year):
        """
        Fetch detailed information about the rules for a specified major and year, including unit codes and credit points.
        
        Parameters:
            major (str): The name of the major.
            year (int): The year of the major.
            
        Returns:
            list: A list containing rule details along with unit codes and credit points for each unit.
        """

        cursor = self.conn.cursor()
        """Fetches the rules for a major in a given year, including the unit codes for each rule and credit points for each unit (if available)"""
        cursor.execute("""
            SELECT r.*, GROUP_CONCAT(u.UNIT_CODE), GROUP_CONCAT(u.CREDIT_PTS)
            FROM Rules r
            INNER JOIN MajorRules rm ON r.rule_id = rm.rule_id
            LEFT JOIN RuleUnits ur ON r.rule_id = ur.rule_id
            LEFT JOIN Units u ON ur.unit_code = u.unit_code
            INNER JOIN Major m ON rm.major_id = m.major_ID
            WHERE m.name = ? AND m.year = ?
            GROUP BY r.rule_id
            """, (major, year))
        rows = cursor.fetchall()
        results = []
        for row in rows:
            rule_id = row[0]
            credit_points = row[1]
            
            # Check if the rule has associated units
            if row[2] and row[3]:
                unit_names = row[2].split(',')
                unit_credits = list(map(int, row[3].split(',')))

                # Zip unit_names and unit_credits into a list of tuples
                unit_list = list(zip(unit_names, unit_credits))
            else:
                unit_list = []

            # Create the final dictionary for each rule
            results.append((rule_id, credit_points, unit_list))

        return results


    def get_major_id(self, major, year):
        """
        Fetch the ID of a major based on its name and year.
        
        Parameters:
            major (str): The name of the major.
            year (int): The year of the major.
            
        Returns:
            int: The ID of the major.
        """

        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT major_id from Major where year=? AND name = ?", (year, major))

        rows = cursor.fetchall()
        print(rows)
        return rows[0][0]

    def fetch_all_rules(self):
        """
        Fetch all rules from the Rules table in the database.
        
        Returns:
            list: A list of tuples containing all rules from the Rules table.
        """

        cursor = self.conn.cursor()
        cursor.execute("SELECT * from Rules")

        rows = cursor.fetchall()
        results = [row for row in rows]
        return results

    def fetch_all_majors(self):
        """
        Fetch all majors, including their names and years, from the Major table.
        
        Returns:
            list: A list of tuples containing the name and year for all majors.
        """

        cursor = self.conn.cursor()
        cursor.execute("SELECT name, year from Major")

        rows = cursor.fetchall()
        results = [row for row in rows]
        return results

    def fetch_unit_rules(self, rule_id):
        """
        Fetch all unit codes associated with a specific rule ID.
        
        Parameters:
            rule_id (int): The ID of the rule.
            
        Returns:
            list: A list of unit codes associated with the given rule ID.
        """

        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT unit_code from RuleUnits where rule_id = ?", (rule_id,))

        rows = cursor.fetchall()
        results = [row[0] for row in rows]
        return results

    def unit_in_major(self, unit_code, major):
        """
        Determine whether a specified unit, identified by its code, is part of a specified major.
        
        Parameters:
            unit_code (str): The code of the unit.
            major (str): The name of the major.
            
        Returns:
            bool: True if the unit is part of the major, False otherwise.
        """

        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT U.unit_code
            FROM Units U
            JOIN RuleUnits RU ON U.unit_code = RU.unit_code
            JOIN Rules R ON RU.rule_id = R.rule_id
            JOIN MajorRules MR ON R.rule_id = MR.rule_id
            JOIN Major M ON MR.major_id = M.major_id
            WHERE U.unit_code = ? AND M.name = ?
        """, (unit_code, major))

        rows = cursor.fetchall()
        return len(rows) > 0

    def create_rule_with_units(self, units, credit_points):
        """
        Create a new rule with specified credit points, and assigns units to this rule.
        
        Parameters:
            units (list): A list of unit codes to be assigned to the rule.
            credit_points (int): The number of credit points for the rule.
            
        Returns:
            int: The ID of the newly created rule.
        """

        # 1. creates a rule with the right credit_points
        # 2. then for each unit, assigns the unit to the rule
        rule_id = self.create_rule_and_get_id(credit_points)
        for unit in units:
            self.link_unit_rule(unit, rule_id)

        return rule_id

    def create_major_with_rules(self, major, year, rules):
        """
        Create a new major for a specified year and assigns rules to it.
        
        Parameters:
            major (str): The name of the major.
            year (int): The year for the major.
            rules (list): A list of rule IDs to be assigned to the major.
        """

        # 1. creates a major with the right year
        # 2. then for each rule, assigns the rule to the major
        major_id = self.create_major_and_get_id(major, year)
        for rule in rules:
            self.link_major_rule(major_id, rule)

    # Given a major name, returns all the major ids
    def get_major_ids(self, major):
        """
        Fetch the IDs of all majors with a specified name.
        
        Parameters:
            major (str): The name of the major.
            
        Returns:
            list: A list of major IDs associated with the given name.
        """

        cursor = self.conn.cursor()
        cursor.execute("SELECT major_id from Major where name = ?", (major,))

        rows = cursor.fetchall()
        results = [row[0] for row in rows]
        return results
