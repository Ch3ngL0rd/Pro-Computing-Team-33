import sqlite3

# Connect to an in-memory SQLite database

class Sqlite_handbookDB():
    def __init__(self) -> None:
        self.conn = sqlite3.connect(':memory:')
        self.create_db()

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
        CREATE TABLE RuleUnits (
            unit_code TEXT,
            rule_id INTEGER,
            FOREIGN KEY(unit_code) REFERENCES Units(unit_code) ON DELETE CASCADE,
            FOREIGN KEY(rule_id) REFERENCES Rule(rule_id),
            PRIMARY KEY(unit_code, rule_id)
        );
        ''')
    
        cursor.execute('''
        CREATE TABLE Rules (
            rule_id INTEGER PRIMARY KEY AUTOINCREMENT,
            value INTEGER
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
            FOREIGN KEY(major_id) REFERENCES Major(major_id),
            FOREIGN KEY(rule_id) REFERENCES Rules(rule_id),
            PRIMARY KEY(major_id, rule_id)
        );
        ''')

    def duplicate_major(self, src_major, src_yr, nw_major, nw_yr):
        cursor = self.conn.cursor()
        self.create_major(cursor, nw_major, nw_yr)
        nw_major_id = cursor.lastrowid
        
        #Get a list of all rules for the current major
        rules_to_create = self.fetch_major_rules(cursor, src_major, src_yr)
        
        #Iterate through every rule that needs to be created
        for rule in rules_to_create:
            self.create_rule(cursor, rule[1])
            new_rule_id = cursor.lastrowid
            self.link_major_rule(cursor,nw_major_id,new_rule_id)
            
            #Get all units to link
            units_to_link = self.fetch_unit_rules(cursor, rule[0])
            for unit in units_to_link:
                self.link_unit_rule(cursor, unit, new_rule_id)


    def select_all_rules(self, major, yr):
        #Gets cursor for conn
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
            #Extract values from row
            rule_value, unit_codes = row
            unit_codes_list = unit_codes.split(',')  # Split the comma-separated unit codes
            output.append((rule_value, unit_codes_list)) #Append to output list

        return output
  

    def select_all_major_units(self, major, yr):
        #Gets cursor for conn
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

        #Creates a new unit in the major database based off of provided code/credit pts
        cursor.execute("INSERT INTO Units(unit_code, credit_pts) VALUES(?, ?)", (unit_code, credit_pts))
    

    def create_rule(self, rule_value):
        cursor = self.conn.cursor()

        cursor.execute("INSERT INTO Rules(value) VALUES(?)", (rule_value,))
    

    def link_unit_rule(self, unit_code, rule_id):
        cursor = self.conn.cursor()

        cursor.execute("INSERT INTO RuleUnits(unit_code, rule_id) VALUES(?, ?)", (unit_code, rule_id))
    

    def create_major(self, major_name, major_year):
        cursor = self.conn.cursor()

        cursor.execute("INSERT INTO Major(name, year) VALUES(?,?)", (major_name, major_year))
    

    def link_major_rule(self, major_id, rule_id):
        cursor = self.conn.cursor()

        cursor.execute("INSERT INTO MajorRules(major_id, rule_id) VALUES(?,?)", (major_id,rule_id))
    

    def unlink_unit_rule(self, unit_code, rule_id):
        cursor = self.conn.cursor()

        cursor.execute("DELETE FROM RuleUnits where unit_code = ? AND rule_id = ?", (unit_code, rule_id))


    def unlink_major_rule(self, name, yr, rule_id):
        cursor = self.conn.cursor()
        
        cursor.execute("SELECT major_id from Major where name = ? and year = ?", (name, yr))
        results = cursor.fetchall()
        major_id = results[0][0]
        
        cursor.execute("DELETE FROM MajorRules where major_id = ? AND rule_id = ?", (major_id, rule_id))


    def delete_unit(cursor, unit_code):
        cursor.execute("DELETE FROM units where unit_code=?", (unit_code,))


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
        """ Fetches the rules for a major in a given year, including the unit codes for each rule and credit points for each unit"""
        cursor.execute("""
            SELECT r.*, GROUP_CONCAT(u.UNIT_CODE), GROUP_CONCAT(u.CREDIT_PTS)
            FROM Rules r
            INNER JOIN MajorRules rm ON r.rule_id = rm.rule_id
            INNER JOIN RuleUnits ur ON r.rule_id = ur.rule_id
            INNER JOIN Units u ON ur.unit_code = u.unit_code
            INNER JOIN Major m ON rm.major_id = m.major_ID
            WHERE m.name = ? AND m.year = ?
            GROUP BY r.rule_id
            """, (major, year))
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
            results.append((rule_id,credit_points, unit_list))

        return results


    def get_major_id(self, major, year):
        cursor = self.conn.cursor()
        cursor.execute("SELECT major_id from Major where year=? AND name = ?", (year, major))

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
        cursor.execute("SELECT unit_code from RuleUnits where rule_id = ?", (rule_id,))

        rows = cursor.fetchall()
        results = [row[0] for row in rows]
        return results
    

    def populate_sampleDB(self):

        # Insert Sample Data
        self.create_unit('ENSC1003', 6)
        self.create_unit('CITS2401', 6)
        self.create_unit('MATH1011', 6)
        self.create_unit('GENG3402', 6)
        self.create_unit('MATH3023', 6)
        self.create_unit('MECH3001', 6)
        self.create_unit('MECH3002', 6)
        self.create_unit('MECH3024', 6)
        self.create_unit('MECH3424', 6)
        self.create_unit('GENG3000', 6)
        self.create_unit('GENG5010', 6)
        self.create_unit('GENG5507', 6)
        self.create_unit('MECH4426', 6)
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
        self.create_rule(6)
        self.create_rule(18)
        self.create_rule(12)
        self.create_rule(24)
        self.create_major('Computer Science', 2023)
        self.create_major('Computer Science', 2022)

        #Link sample data
        self.link_unit_rule('CITS2401', 1)
        self.link_unit_rule('ENSC1003',2)
        self.link_unit_rule('CITS2401',2)
        self.link_unit_rule('MATH1011',2)
        self.link_unit_rule('CITS2401',3)
        self.link_unit_rule('MATH1011',3)

    
        self.link_major_rule(1,1)
        self.link_major_rule(1,3)
        self.link_major_rule(1,2)
        self.link_major_rule(2,2)
        self.link_major_rule(2,3)
        self.link_major_rule(2,4)

        self.link_unit_rule('GENG3402', 1)
        self.link_unit_rule('MATH3023', 1)
        self.link_unit_rule('MECH3001', 1)
        self.link_unit_rule('MECH3002', 1)
        self.link_unit_rule('MECH3024', 1)
        self.link_unit_rule('MECH3424', 1)
        self.link_unit_rule('GENG3000', 1)
        self.link_unit_rule('GENG5010', 1)
        self.link_unit_rule('GENG5507', 1)
        self.link_unit_rule('MECH4426', 1)
        self.link_unit_rule('MECH4502', 1)
        self.link_unit_rule('MECH5551', 1)
        self.link_unit_rule('GENG4411', 1)
        self.link_unit_rule('GENG4412', 1)
        self.link_unit_rule('MECH5552', 1)
        self.link_unit_rule('CHPR3405', 1)
        self.link_unit_rule('GENG5504', 1)
        self.link_unit_rule('GENG5505', 1)
        self.link_unit_rule('GENG5514', 1)
        self.link_unit_rule('MECH4428', 1)
        self.link_unit_rule('MECH5504', 1)
        self.create_major('Math', 2023)
