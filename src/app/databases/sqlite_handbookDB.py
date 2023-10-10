import sqlite3

# Connect to an in-memory SQLite database


class Sqlite_handbookDB():
    def __init__(self, handbook_db_path) -> None:
        #self.conn = sqlite3.connect(':memory:')
        self.conn = sqlite3.connect(handbook_db_path)
        #self.create_db()

    def db_commit(self):
        """Commit changes to the database."""
        try:
            self.conn.commit()
            self.conn.close()
            print("Changes committed to the database.")
        except Exception as e:
            print(f"Error committing changes: {e}")

    def create_db(self):
        cursor = self.conn.cursor()

        # Create Tables
        cursor.execute('''
        CREATE TABLE Units (
            unit_code TEXT PRIMARY KEY,
            credit_pts INTEGER
        );
        ''')

        cursor.execute('''
        CREATE TABLE Groups (
            group_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT
        );
        ''')

        cursor.execute('''
        CREATE TABLE Rules (
            rule_id INTEGER PRIMARY KEY AUTOINCREMENT,
            value INTEGER
        );
        ''')

        cursor.execute('''
        CREATE TABLE RuleUnits (
            unit_code TEXT,
            rule_id INTEGER,
            FOREIGN KEY(unit_code) REFERENCES Units(unit_code) ON DELETE CASCADE,
            FOREIGN KEY(rule_id) REFERENCES Rules(rule_id),
            PRIMARY KEY(unit_code, rule_id)
        );
        ''')

        cursor.execute('''
        CREATE TABLE Major (
            major_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            year INTEGER
        );
        ''')

        cursor.execute('''
            CREATE TABLE MajorRules (
                major_id INTEGER,
                rule_id INTEGER,
                FOREIGN KEY(major_id) REFERENCES Major(major_id) ON DELETE CASCADE,
                FOREIGN KEY(rule_id) REFERENCES Rules(rule_id),
                PRIMARY KEY(major_id, rule_id)
            );
            ''')

    def duplicate_major(self, src_major, src_yr, nw_major, nw_yr):
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
        cursor = self.conn.cursor()

        cursor.execute("INSERT INTO Rules(value) VALUES(?)", (rule_value,))

        return cursor

    def create_rule_and_get_id(self, rule_value):
        cursor = self.conn.cursor()

        # Insert the new rule
        cursor.execute("INSERT INTO Rules(value) VALUES(?)", (rule_value,))
        self.conn.commit()  # Commit the transaction

        # Get the ID of the last inserted rule
        rule_id = cursor.lastrowid

        return rule_id

    def link_unit_rule(self, unit_code, rule_id):
        cursor = self.conn.cursor()

        cursor.execute(
            "INSERT INTO RuleUnits(unit_code, rule_id) VALUES(?, ?)", (unit_code, rule_id))

    def create_major(self, major_name, major_year):
        cursor = self.conn.cursor()

        cursor.execute("INSERT INTO Major(name, year) VALUES(?,?)",
                       (major_name, major_year))

        return cursor

    def create_major_and_get_id(self, major_name, major_year):
        cursor = self.conn.cursor()

        # Insert the new major
        cursor.execute("INSERT INTO Major(name, year) VALUES(?,?)",
                       (major_name, major_year))

        self.conn.commit()

        # Get the ID of the last inserted major
        major_id = cursor.lastrowid
        return major_id

    def link_major_rule(self, major_id, rule_id):
        cursor = self.conn.cursor()

        cursor.execute(
            "INSERT INTO MajorRules(major_id, rule_id) VALUES(?,?)", (major_id, rule_id))

    def unlink_unit_rule(self, unit_code, rule_id):
        cursor = self.conn.cursor()

        cursor.execute(
            "DELETE FROM RuleUnits where unit_code = ? AND rule_id = ?", (unit_code, rule_id))

    def unlink_major_rule(self, name, yr, rule_id):
        cursor = self.conn.cursor()

        cursor.execute(
            "SELECT major_id from Major where name = ? and year = ?", (name, yr))
        results = cursor.fetchall()
        major_id = results[0][0]

        cursor.execute(
            "DELETE FROM MajorRules where major_id = ? AND rule_id = ?", (major_id, rule_id))

    def delete_unit(self, unit_code):
        cursor = self.conn.cursor()

        cursor.execute("DELETE FROM units where unit_code=?", (unit_code,))

    def delete_major(self, major_id):
        cursor = self.conn.cursor()
        
        cursor.execute("DELETE FROM Major WHERE major_id=?", (major_id,))

        # deletes rules as well
        cursor.execute("DELETE FROM MajorRules WHERE major_id=?", (major_id,))

    def fetch_all_units(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT unit_code FROM units")
        rows = cursor.fetchall()
        results = [row[0] for row in rows]
        return results

    def fetch_all_units_with_credit(self):
        cursor = self.conn.cursor()

        cursor.execute("SELECT unit_code, credit_pts FROM units")
        rows = cursor.fetchall()
        results = [row for row in rows]
        return results

    def fetch_major_rules(self, major, year):
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
        cursor = self.conn.cursor()
        cursor.execute("""SELECT m.name, m.year
                       FROM Rules r
                       INNER JOIN MajorRules rm on r.rule_id = rm.rule_id
                       INNER JOIN Major m on rm.major_id = m.major_ID
                       WHERE r.rule_id = ?""", (rule_id,))
        
        rows = cursor.fetchall()
        return (rows[0][0], rows[0][1])
        
    def fetch_rule_verbose(self, rule_id):
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
        cursor = self.conn.cursor()

        cursor.execute("DELETE FROM Rules where rule_id = ?", (rule_id,))

    def fetch_years(self):
        cursor = self.conn.cursor()

        cursor.execute("SELECT DISTINCT year from Major")
        rows = cursor.fetchall()
        results = [row[0] for row in rows]
        return results

    def fetch_majors_for_year(self, year):
        cursor = self.conn.cursor()

        cursor.execute("SELECT name from Major where year = ?", (year,))
        rows = cursor.fetchall()
        results = [row[0] for row in rows]
        return results

    def fetch_major_rules_verbose(self, major, year):
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
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT major_id from Major where year=? AND name = ?", (year, major))

        rows = cursor.fetchall()
        print(rows)
        return rows[0][0]

    def fetch_all_rules(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * from Rules")

        rows = cursor.fetchall()
        results = [row for row in rows]
        return results

    def fetch_all_majors(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT name, year from Major")

        rows = cursor.fetchall()
        results = [row for row in rows]
        return results

    def fetch_unit_rules(self, rule_id):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT unit_code from RuleUnits where rule_id = ?", (rule_id,))

        rows = cursor.fetchall()
        results = [row[0] for row in rows]
        return results

    def unit_in_major(self, unit_code, major):
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
        # 1. creates a rule with the right credit_points
        # 2. then for each unit, assigns the unit to the rule
        rule_id = self.create_rule_and_get_id(credit_points)
        for unit in units:
            self.link_unit_rule(unit, rule_id)

        return rule_id

    def create_major_with_rules(self, major, year, rules):
        # 1. creates a major with the right year
        # 2. then for each rule, assigns the rule to the major
        major_id = self.create_major_and_get_id(major, year)
        for rule in rules:
            self.link_major_rule(major_id, rule)

    # Given a major name, returns all the major ids
    def get_major_ids(self, major):
        cursor = self.conn.cursor()
        cursor.execute("SELECT major_id from Major where name = ?", (major,))

        rows = cursor.fetchall()
        results = [row[0] for row in rows]
        return results
    
    def create_all_units(self):
                # Chemical Engineering
        self.create_unit('CHEM1001', 6)
        self.create_unit('CHEM1002', 6)
        self.create_unit('CHPR1005', 6)
        self.create_unit('ENSC1004', 6)
        self.create_unit('GENG1000', 0)
        self.create_unit('GENG1010', 6)
        self.create_unit('MATH1011', 6)
        self.create_unit('MATH1012', 6)
        self.create_unit('PHYS1001', 6)

        # Take 30 points
        self.create_unit('CHPR2006', 6)
        self.create_unit('CHPR2007', 6)
        self.create_unit('CHPR2018', 6)
        self.create_unit('CITS2401', 6)
        self.create_unit('GENG2000', 0)
        self.create_unit('GENG2003', 6)

        # Take 42 points
        self.create_unit('CHPR3018', 6)
        self.create_unit('CHPR3019', 6)
        self.create_unit('CHPR3404', 6)
        self.create_unit('CHPR3405', 6)
        self.create_unit('CHPR3406', 6)
        self.create_unit('CHPR3407', 6)
        self.create_unit('GENG3000', 0)
        self.create_unit('GENG3402', 6)
        self.create_unit('GENG5010', 0)

        # Level 4
        self.create_unit('CHPR4501', 6)
        self.create_unit('CHPR5550', 12)
        self.create_unit('GENG4411', 6)
        self.create_unit('GENG4412', 6)
        self.create_unit('GENG5507', 6)

        # Group A
        self.create_unit('CHPR4408', 6)
        self.create_unit('CHPR5520', 6)
        self.create_unit('CHPR5521', 6)
        self.create_unit('CHPR5522', 6)
        self.create_unit('GENG5516', 6)

        # Group B
        self.create_unit('CITS4009', 6)
        self.create_unit('ENVE4401', 6)
        self.create_unit('GENG4403', 6)
        self.create_unit('GENG4410', 6)
        self.create_unit('GENG5503', 6)
        self.create_unit('GENG5504', 6)
        self.create_unit('GENG5506', 6)

        # Mechanical Engineering Units
        self.create_unit('ENSC1004', 6)
        self.create_unit('GENG1000', 0)
        self.create_unit('GENG1010', 6)
        self.create_unit('GENG1101', 6)
        self.create_unit('MATH1011', 6)
        self.create_unit('MATH1012', 6)
        self.create_unit('PHYS1001', 6)
        self.create_unit('CITS2401', 6)
        self.create_unit('ENSC2003', 6)
        self.create_unit('ENSC2004', 6)
        self.create_unit('GENG2000', 0)
        self.create_unit('GENG2003', 6)
        self.create_unit('GENG2004', 6)
        self.create_unit('MECH2002', 6)
        self.create_unit('MECH2004', 6)

        self.create_unit('GENG3000', 0)
        self.create_unit('GENG3402', 6)
        self.create_unit('GENG3405', 6)
        self.create_unit('MATH3023', 6)
        self.create_unit('MECH3001', 6)
        self.create_unit('MECH3002', 6)
        self.create_unit('MECH3024', 6)
        self.create_unit('MECH3424', 6)
        self.create_unit('GENG5010', 0)
        self.create_unit('GENG5507', 6)
        self.create_unit('MECH4426', 6)
        self.create_unit('MECH4429', 6)
        self.create_unit('MECH4502', 6)
        self.create_unit('MECH5551', 6)
        self.create_unit('GENG4411', 6)
        self.create_unit('GENG4412', 6)
        self.create_unit('MECH5552', 6)
        self.create_unit('CHPR3405', 6)
        self.create_unit('GENG5504', 6)
        self.create_unit('GENG5505', 6)
        self.create_unit('GENG5514', 6)
        self.create_unit('MECH4428', 6)
        self.create_unit('MECH5504', 6)

        # Civil Engineering Units
        self.create_unit('GENG1000', 0)
        self.create_unit('GENG1010', 6)
        self.create_unit('GENG1014', 6)
        self.create_unit('MATH1011', 6)
        self.create_unit('MATH1012', 6)
        self.create_unit('PHYS1001', 6)

        self.create_unit('CITS2401', 6)
        self.create_unit('CIVL2008', 6)
        self.create_unit('CIVL2551', 6)
        self.create_unit('ENSC2004', 6)
        self.create_unit('GENG2000', 0)
        self.create_unit('GENG2004', 6)
        self.create_unit('GENG2009', 6)
        self.create_unit('GENG2010', 6)
        self.create_unit('GENG2012', 6)

        self.create_unit('CIVL3401', 6)
        self.create_unit('CIVL3402', 6)
        self.create_unit('CIVL3403', 6)
        self.create_unit('CIVL3404', 6)
        self.create_unit('GENG3000', 0)
        self.create_unit('GENG3405', 6)

        self.create_unit('CIVL4430', 6)
        self.create_unit('GENG4411', 6)
        self.create_unit('GENG4412', 6)
        self.create_unit('GENG5010', 0)
        self.create_unit('GENG5505', 6)
        self.create_unit('GENG5507', 6)

        self.create_unit('CIVL5550', 6)
        self.create_unit('CIVL5552', 6)

        self.create_unit('CIVL5501', 6)
        self.create_unit('CIVL5503', 6)
        self.create_unit('CIVL5504', 6)
        self.create_unit('CIVL5505', 6)
        self.create_unit('ENVE3402', 6)
        self.create_unit('GENG5501', 6)
        self.create_unit('GENG5502', 6)
        self.create_unit('GENG5514', 6)

        # Mining Engineering Units
        # Level 1 Units
        self.create_unit('CHEM1001', 6)
        self.create_unit('EART1104', 6)
        self.create_unit('GENG1000', 0)
        self.create_unit('GENG1010', 6)
        self.create_unit('GENG1014', 6)
        self.create_unit('MATH1011', 6)
        self.create_unit('MATH1012', 6)
        self.create_unit('PHYS1001', 6)

        # Level 2 Units
        self.create_unit('CITS2401', 6)
        self.create_unit('ENSC2003', 6)
        self.create_unit('ENSC2004', 6)
        self.create_unit('GENG2000', 0)
        self.create_unit('GENG2004', 6)
        self.create_unit('GENG2009', 6)
        self.create_unit('GENG2010', 6)
        self.create_unit('MINE2001', 6)

        # Level 3 Units
        self.create_unit('GENG3000', 0)
        self.create_unit('MINE3401', 6)
        self.create_unit('MINE3404', 6)
        self.create_unit('MINE3405', 6)
        self.create_unit('MINE3406', 6)
        self.create_unit('MINE3503', 6)

        # Level 4 Units
        self.create_unit('GENG4403', 6)
        self.create_unit('GENG4411', 6)
        self.create_unit('GENG4412', 6)
        self.create_unit('GENG5010', 0)
        self.create_unit('GENG5505', 6)
        self.create_unit('GENG5507', 6)
        self.create_unit('MINE4001', 6)
        self.create_unit('MINE4502', 6)
        self.create_unit('MINE5501', 6)
        self.create_unit('MINE5551', 6)

        # Software Engineering Units
        # Level 1 Units
        self.create_unit('CITS1003', 6)
        self.create_unit('CITS1401', 6)
        self.create_unit('CITS1402', 6)
        self.create_unit('ELEC1303', 6)
        self.create_unit('GENG1000', 0)
        self.create_unit('GENG1010', 6)
        self.create_unit('MATH1011', 6)
        self.create_unit('MATH1012', 6)
        self.create_unit('PHYS1001', 6)

        # Level 2 Units
        self.create_unit('CITS2002', 6)
        self.create_unit('CITS2005', 6)
        self.create_unit('CITS2200', 6)
        self.create_unit('CITS2211', 6)
        self.create_unit('GENG2000', 0)
        self.create_unit('STAT2063', 6)

        # Level 3 Units
        self.create_unit('CITS3002', 6)
        self.create_unit('CITS3005', 6)
        self.create_unit('CITS3007', 6)
        self.create_unit('CITS3200', 6)
        self.create_unit('CITS3301', 6)
        self.create_unit('CITS3403', 6)
        self.create_unit('ELEC3020', 6)
        self.create_unit('GENG3000', 0)

        # Level 4 Units
        self.create_unit('CITS4419', 6)
        self.create_unit('CITS5501', 6)
        self.create_unit('CITS5503', 6)
        self.create_unit('CITS5507', 6)
        self.create_unit('GENG4411', 6)
        self.create_unit('GENG4412', 6)
        self.create_unit('GENG5010', 0)
        self.create_unit('GENG5505', 6)
        self.create_unit('GENG5507', 6)

        # Automation and Robotics Engineering Units
        # Level 1 Units
        self.create_unit('CITS1401', 6)
        self.create_unit('ELEC1303', 6)
        self.create_unit('ENSC1004', 6)
        self.create_unit('GENG1000', 0)
        self.create_unit('GENG1010', 6)
        self.create_unit('MATH1011', 6)
        self.create_unit('MATH1012', 6)

        # Level 2 Units
        self.create_unit('CITS2002', 6)
        self.create_unit('CITS2200', 6)
        self.create_unit('ELEC2311', 6)
        self.create_unit('ENSC2003', 6)
        self.create_unit('ENSC2004', 6)
        self.create_unit('GENG2000', 0)
        self.create_unit('GENG2004', 6)
        self.create_unit('MECH2004', 6)

        # Level 3 Units
        self.create_unit('AUTO3002', 6)
        self.create_unit('CITS3001', 6)
        self.create_unit('ELEC3016', 6)
        self.create_unit('ELEC3020', 6)
        self.create_unit('GENG3000', 0)
        self.create_unit('GENG3402', 6)
        self.create_unit('MECH3001', 6)
        self.create_unit('MECH3424', 6)

        # Level 4 Units
        self.create_unit('AUTO4507', 6)
        self.create_unit('AUTO4508', 6)
        self.create_unit('CITS4402', 6)
        self.create_unit('ELEC5506', 6)
        self.create_unit('GENG4411', 6)
        self.create_unit('GENG4412', 6)
        self.create_unit('GENG5010', 0)
        self.create_unit('GENG5505', 6)
        self.create_unit('GENG5507', 6)

        # Biomedical Engineering Units
        # Level 1 Units
        self.create_unit('CITS1401', 6)
        self.create_unit('ENSC1004', 6)
        self.create_unit('GENG1000', 0)
        self.create_unit('GENG1010', 6)
        self.create_unit('GENG1101', 6)
        self.create_unit('IMED1001', 6)
        self.create_unit('MATH1011', 6)
        self.create_unit('MATH1012', 6)
        self.create_unit('PHYS1001', 6)

        # Level 2 Units
        self.create_unit('CITS2200', 6)
        self.create_unit('ENSC2003', 6)
        self.create_unit('ENSC2004', 6)
        self.create_unit('GENG2000', 0)
        self.create_unit('GENG2003', 6)
        self.create_unit('GENG2004', 6)
        self.create_unit('MECH2002', 6)
        self.create_unit('PHYL2002', 6)

        # Level 3 Units
        self.create_unit('BMEG3001', 6)
        self.create_unit('BMEG3002', 6)
        self.create_unit('ELEC3020', 6)
        self.create_unit('ELEC3021', 6)
        self.create_unit('GENG3000', 0)
        self.create_unit('MECH3424', 6)

        # Level 4 Units
        self.create_unit('BMEG4001', 6)
        self.create_unit('BMEG4003', 6)
        self.create_unit('BMEG5001', 6)
        self.create_unit('BMEG5551', 6)
        self.create_unit('BMEG5552', 6)
        self.create_unit('GENG4411', 6)
        self.create_unit('GENG4412', 6)
        self.create_unit('GENG5010', 0)
        self.create_unit('GENG5505', 6)

        # Electrical and Electronic Engineering
        # Level 1 Units
        self.create_unit('ELEC1303', 6)
        self.create_unit('GENG1000', 0)
        self.create_unit('GENG1010', 6)
        self.create_unit('MATH1011', 6)
        self.create_unit('MATH1012', 6)
        self.create_unit('PHYS1001', 6)

        # Level 2 Units
        self.create_unit('CITS2401', 6)
        self.create_unit('ELEC2311', 6)
        self.create_unit('ENSC2003', 6)
        self.create_unit('ENSC2004', 6)
        self.create_unit('GENG2000', 0)
        self.create_unit('PHYS2003', 6)
        self.create_unit('STAT2063', 6)

        # Level 3 Units
        self.create_unit('ELEC3014', 6)
        self.create_unit('ELEC3015', 6)
        self.create_unit('ELEC3016', 6)
        self.create_unit('ELEC3020', 6)
        self.create_unit('ELEC3021', 6)
        self.create_unit('GENG3000', 0)
        self.create_unit('GENG3402', 6)
        self.create_unit('MATH3023', 6)

        # Level 4 Units
        self.create_unit('ELEC4401', 6)
        self.create_unit('ELEC4402', 6)
        self.create_unit('ELEC4404', 6)
        self.create_unit('ELEC4407', 6)
        self.create_unit('ELEC4505', 6)
        self.create_unit('ELEC5506', 6)
        self.create_unit('ELEC5552', 6)
        self.create_unit('GENG4411', 6)
        self.create_unit('GENG4412', 6)
        self.create_unit('GENG5010', 0)
        self.create_unit('GENG5505', 6)

        # Environmental Engineering
        # Level 1 Units
        self.create_unit('CHEM1001', 6)
        self.create_unit('GENG1000', 0)
        self.create_unit('GENG1010', 6)
        self.create_unit('GENG1014', 6)
        self.create_unit('MATH1011', 6)
        self.create_unit('MATH1012', 6)
        self.create_unit('PHYS1001', 6)

        # Level 2 Units
        self.create_unit('CITS2401', 6)
        self.create_unit('ENSC2004', 6)
        self.create_unit('ENVE2013', 6)
        self.create_unit('ENVE2606', 6)
        self.create_unit('ENVE2607', 6)
        self.create_unit('ENVT2251', 6)
        self.create_unit('GENG2000', 0)
        self.create_unit('GENG2010', 6)
        self.create_unit('GENG2012', 6)
        self.create_unit('GEOG2201', 6)

        # Level 3 Units
        self.create_unit('ENVE3402', 6)
        self.create_unit('ENVE3403', 6)
        self.create_unit('ENVE3405', 6)
        self.create_unit('ENVE3608', 6)
        self.create_unit('ENVE3609', 6)
        self.create_unit('GENG3000', 0)

        # Level 4 Units
        self.create_unit('ENVE4401', 6)
        self.create_unit('ENVE4601', 6)
        self.create_unit('ENVE5502', 6)
        self.create_unit('ENVE5551', 6)
        self.create_unit('ENVE5552', 6)
        self.create_unit('GENG4411', 6)
        self.create_unit('GENG4412', 6)
        self.create_unit('GENG5010', 0)
        self.create_unit('GENG5501', 6)



    def populate_sampleDB(self):

        self.create_all_units()
        # Insert Sample Data

        # Engineering Majors - still to add 2023
        # self.create_major('Environmental Engineering', 2023)

        # Biomedical Engineering Units
        self.create_major_with_rules('Biomedical Engineering', 2023,
                                     [
                                         self.create_rule_with_units(
                                             ['CITS1401', 'ENSC1004', 'GENG1000', 'GENG1010', 'GENG1101', 'IMED1001', 'MATH1011', 'MATH1012', 'PHYS1001'], 48),
                                         self.create_rule_with_units(
                                             ['CITS2200', 'ENSC2003', 'ENSC2004', 'GENG2000', 'GENG2003', 'GENG2004', 'MECH2002', 'PHYL2002'], 42),
                                         self.create_rule_with_units(
                                             ['BMEG3001', 'BMEG3002', 'ELEC3020', 'ELEC3021', 'GENG3000', 'MECH3424'], 30),
                                         self.create_rule_with_units(
                                             ['BMEG4001', 'BMEG4003', 'BMEG5001', 'BMEG5551', 'BMEG5552', 'GENG4411', 'GENG4412', 'GENG5010', 'GENG5505'], 48)
                                     ])

        # Automation and Robotics Engineering 2023
        self.create_major_with_rules('Automation and Robotics Engineering', 2023,
                                     [
                                         self.create_rule_with_units(
                                             ['CITS1401', 'ELEC1303', 'ENSC1004', 'GENG1000', 'GENG1010', 'MATH1011', 'MATH1012'], 36),
                                         self.create_rule_with_units(
                                             ['CITS2002', 'CITS2200', 'ELEC2311', 'ENSC2003', 'ENSC2004', 'GENG2000', 'GENG2004', 'MECH2004'], 42),
                                         self.create_rule_with_units(
                                             ['AUTO3002', 'CITS3001', 'ELEC3016', 'ELEC3020', 'GENG3000', 'GENG3402', 'MECH3001', 'MECH3424'], 42),
                                         self.create_rule_with_units(
                                             ['AUTO4507', 'AUTO4508', 'CITS4402', 'ELEC5506', 'GENG4411', 'GENG4412', 'GENG5010', 'GENG5505', 'GENG5507'], 48)
                                     ])

        # Mechanical Engineering 2023
        self.create_major_with_rules('Mechanical Engineering', 2023,
                                     [
                                         # level 1 and 2 rules for eligibility check
                                         self.create_rule_with_units(
                                             ['ENSC1004', 'GENG1000', 'GENG1010', 'GENG1101', 'MATH1011', 'MATH1012', 'PHYS1001'], 36),
                                         self.create_rule_with_units(
                                             ['CITS2401', 'ENSC2003', 'ENSC2004', 'GENG2000', 'GENG2003', 'GENG2004', 'MECH2002', 'MECH2004'], 42),
                                         # level 3 and above rules
                                         self.create_rule_with_units(
                                             ['GENG3000', 'GENG3402', 'GENG3405', 'MATH3023', 'MECH3001', 'MECH3002', 'MECH3024', 'MECH3424'], 42),
                                         self.create_rule_with_units(
                                             ['GENG5010', 'GENG5507', 'MECH4426', 'MECH4429', 'MECH4502', 'MECH5551'], 30),

                                         self.create_rule_with_units(
                                             ['GENG4411', 'GENG4412', 'MECH5552'], 6),
                                         self.create_rule_with_units(
                                             ['CHPR3405', 'GENG5504', 'GENG5505', 'GENG5514', 'MECH442', 'MEC5504'], 6),
                                         self.create_rule_with_units(
                                             ['GENG4411', 'GENG4412', 'MECH5552', 'CHPR3405', 'GENG5504', 'GENG5505', 'GENG5514', 'MECH442', 'MEC5504'], 18)

                                     ])

        self.create_major_with_rules('Software Engineering', 2023,
                                     [
                                         self.create_rule_with_units(
                                             ['CITS1003', 'CITS1401', 'CITS1402', 'ELEC1303', 'GENG1000', 'GENG1010', 'MATH1011', 'MATH1012', 'PHYS1001'], 48),
                                         self.create_rule_with_units(
                                             ['CITS2002', 'CITS2005', 'CITS2200', 'CITS2211', 'GENG2000', 'STAT2063'], 30),
                                         self.create_rule_with_units(
                                             ['CITS3002', 'CITS3005', 'CITS3007', 'CITS3200', 'CITS3301', 'CITS3403', 'ELEC3020', 'GENG3000'], 42),
                                         self.create_rule_with_units(
                                             ['CITS4419', 'CITS5501', 'CITS5503', 'CITS5507', 'GENG4411', 'GENG4412', 'GENG5010', 'GENG5505', 'GENG5507'], 48)
                                     ])

        self.create_major_with_rules('Mining Engineering', 2023,
                                     [
                                         # Level 1 Units
                                         self.create_rule_with_units(
                                             ['CHEM1001', 'EART1104', 'GENG1000', 'GENG1010', 'GENG1014', 'MATH1011', 'MATH1012', 'PHYS1001'], 42),
                                         # Level 2 Units
                                         self.create_rule_with_units(
                                             ['CITS2401', 'ENSC2003', 'ENSC2004', 'GENG2000', 'GENG2004', 'GENG2009', 'GENG2010', 'MINE2001'], 42),
                                         # Level 3 Units
                                         self.create_rule_with_units(
                                             ['GENG3000', 'MINE3401', 'MINE3404', 'MINE3405', 'MINE3406', 'MINE3503'], 30),
                                         # Level 4 Units
                                         self.create_rule_with_units(
                                             ['GENG4403', 'GENG4411', 'GENG4412', 'GENG5010', 'GENG5505', 'GENG5507', 'MINE4001', 'MINE4502', 'MINE5501', 'MINE5551'], 54)
                                     ])

        # Chemical Engineering 2023
        # 48 points Rule
        self.create_major_with_rules('Chemical Engineering', 2023,
                                     [
                                         self.create_rule_with_units(['CHEM1001', 'CHEM1002', 'CHPR1005', 'ENSC1004',
                                                                      'GENG1000', 'GENG1010', 'MATH1011', 'MATH1012', 'PHYS1001'], 48),



                                         # Take 30 points Rule
                                         self.create_rule_with_units(
                                             ['CHPR2006', 'CHPR2007', 'CHPR2018', 'CITS2401', 'GENG2000', 'GENG2003'], 30),

                                         # Take 42 points Rule
                                         self.create_rule_with_units(['CHPR3018', 'CHPR3019', 'CHPR3404', 'CHPR3405',
                                                                      'CHPR3406', 'CHPR3407', 'GENG3000', 'GENG3402', 'GENG5010'], 42),

                                         # Level 4 Rule - 36
                                         self.create_rule_with_units(
                                             ['CHPR4501', 'CHPR5550', 'GENG4411', 'GENG4412', 'GENG5507'], 36),

                                         # Group A Rule
                                         self.create_rule_with_units(
                                             ['CHPR4408', 'CHPR5520', 'CHPR5521', 'CHPR5522', 'GENG5516'], 12),

                                         # Group B Rule
                                         self.create_rule_with_units(
                                             ['CITS4009', 'ENVE4401', 'GENG4403', 'GENG4410', 'GENG5503', 'GENG5504', 'GENG5506'], 12)
                                     ])

        # Civil Engineering 2023
        self.create_major_with_rules('Civil Engineering', 2023,
                                     [
                                         # level 1 and 2 rules for eligibility check
                                         self.create_rule_with_units(
                                             ['GENG1000', 'GENG1010', 'GENG1014', 'MATH1011', 'MATH1012', 'PHYS1001'], 30),
                                         self.create_rule_with_units(
                                             ['CITS2401', 'CIVL2008', 'CIVL2551', 'ENSC2004', 'GENG2000', 'GENG2004', 'GENG2009', 'GENG2010', 'GENG2012'], 42),
                                         # level 3 and above rules
                                         self.create_rule_with_units(
                                             ['CIVL3401', 'CIVL3402', 'CIVL3403', 'CIVL3404', 'GENG3000', 'GENG3405'], 30),
                                         self.create_rule_with_units(
                                             ['CIVL4430', 'GENG4411', 'GENG4412', 'GENG5010', 'GENG5505', 'GENG5507'], 30),

                                         self.create_rule_with_units(
                                             ['CIVL5550', 'CIVL5552'], 6),
                                         self.create_rule_with_units(
                                             ['CIVL5501', 'CIVL5503', 'CIVL5504', 'CIVL5505', 'ENVE3402', 'GENG5501', 'GENG5502', 'GENG5514'], 18),
                                         self.create_rule_with_units(
                                             ['CIVL5550', 'CIVL5552', 'CIVL5501', 'CIVL5503', 'CIVL5504', 'CIVL5505', 'ENVE3402', 'GENG5501', 'GENG5502', 'GENG5514'], 30)
                                     ])

        self.create_major_with_rules('Electrical and Electronic Engineering', 2023,
                                    [
                                        self.create_rule_with_units(['ELEC1303', 'GENG1000', 'GENG1010', 'MATH1011', 'MATH1012', 'PHYS1001'], 30),
                                        self.create_rule_with_units(['CITS2401', 'ELEC2311', 'ENSC2003', 'ENSC2004', 'GENG2000', 'PHYS2003', 'STAT2063'], 36),
                                        self.create_rule_with_units(['ELEC3014', 'ELEC3015', 'ELEC3016', 'ELEC3020', 'ELEC3021', 'GENG3000', 'GENG3402', 'MATH3023'], 42),
                                        self.create_rule_with_units(['ELEC4401', 'ELEC4402', 'ELEC4404', 'ELEC4407', 'ELEC4505', 'ELEC5506', 'ELEC5552', 'GENG4411', 'GENG4412', 'GENG5010', 'GENG5505'], 60)
                                    ])

        self.create_major_with_rules('Environmental Engineering', 2023,
                                    [
                                        self.create_rule_with_units(['CHEM1001', 'GENG1000', 'GENG1010', 'GENG1014', 'MATH1011', 'MATH1012', 'PHYS1001'], 36),
                                        self.create_rule_with_units(['CITS2401', 'ENSC2004', 'ENVE2013', 'ENVE2606', 'ENVE2607', 'ENVT2251', 'GENG2000', 'GENG2010', 'GENG2012', 'GEOG2201'], 54),
                                        self.create_rule_with_units(['ENVE3402', 'ENVE3403', 'ENVE3405', 'ENVE3608', 'ENVE3609', 'GENG3000'], 30),
                                        self.create_rule_with_units(['ENVE4401', 'ENVE4601', 'ENVE5502', 'ENVE5551', 'ENVE5552', 'GENG4411', 'GENG4412', 'GENG5010', 'GENG5501'], 48)
                                    ])
