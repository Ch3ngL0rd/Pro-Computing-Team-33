import sqlite3

# Connect to an in-memory SQLite database
def create_db():
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()

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

    return conn

def select_all_rules(conn, major, yr):

    #Gets cursor for conn
    cursor = conn.cursor()
    
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

def select_all_major_units(conn, major, yr):

    #Gets cursor for conn
    cursor = conn.cursor()
    
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

def create_unit(cursor, unit_code, credit_pts):
    #Creates a new unit in the major database based off of provided code/credit pts
    cursor.execute("INSERT INTO Units(unit_code, credit_pts) VALUES(?, ?)", (unit_code, credit_pts))
    
def create_rule(cursor, rule_value):
    cursor.execute("INSERT INTO Rules(value) VALUES(?)", (rule_value,))
    
def link_unit_rule(cursor, unit_code, rule_id):
    cursor.execute("INSERT INTO RuleUnits(unit_code, rule_id) VALUES(?, ?)", (unit_code, rule_id))
    
def create_major(cursor, major_name, major_year):
    cursor.execute("INSERT INTO Major(name, year) VALUES(?,?)", (major_name, major_year))

def link_major_rule(cursor, major_id, rule_id):
    cursor.execute("INSERT INTO MajorRules(major_id, rule_id) VALUES(?,?)", (major_id,rule_id))
    
def unlink_unit_rule(cursor, unit_code, rule_id):
    cursor.execute("DELETE FROM RuleUnits where unit_code = ? AND rule_id = ?", (unit_code, rule_id))
    
def unlink_major_rule(cursor, name, yr, rule_id):
    cursor.execute("SELECT major_id from Major where name = ? and year = ?", (name, yr))
    results = cursor.fetchall()
    major_id = results[0][0]
    
    cursor.execute("DELETE FROM MajorRules where major_id = ? AND rule_id = ?", (major_id, rule_id))

def delete_unit(cursor, unit_code):
    cursor.execute("DELETE FROM units where unit_code=?", (unit_code,))
  
def fetch_all_units(cursor):
    cursor.execute("SELECT unit_code FROM units")
    rows = cursor.fetchall()
    results = [row[0] for row in rows]
    return results

def fetch_all_units_with_credit(cursor):
    cursor.execute("SELECT unit_code, credit_pts FROM units")
    rows = cursor.fetchall()
    results = [row for row in rows]
    return results

def fetch_major_rules(cursor, major, year):
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

def delete_rule(cursor, rule_id):
    cursor.execute("DELETE FROM Rules where rule_id = ?", (rule_id,))

def fetch_years(cursor):
    cursor.execute("SELECT DISTINCT year from Major")
    rows = cursor.fetchall()
    results = [row[0] for row in rows]
    return results

def fetch_majors_for_year(cursor, year):
    cursor.execute("SELECT name from Major where year = ?", (year,))
    rows = cursor.fetchall()
    results = [row[0] for row in rows]
    return results

def fetch_major_rules_verbose(cursor, major, year):
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


def get_major_id(cursor, major, year):
    cursor.execute("SELECT major_id from Major where year=? AND name = ?", (year, major))
    
    rows = cursor.fetchall()
    print(rows)
    return rows[0][0]
    
def fetch_all_rules(cursor):
    cursor.execute("SELECT * from Rules")
    rows = cursor.fetchall()
    results = [row for row in rows]

    return results

def fetch_all_majors(cursor):
    cursor.execute("SELECT name, year from Major")
    rows = cursor.fetchall()
    
    results = [row for row in rows]
    return results
    

def fetch_unit_rules(cursor, rule_id):
    cursor.execute("SELECT unit_code from RuleUnits where rule_id = ?", (rule_id,))
    rows = cursor.fetchall()
    results = [row[0] for row in rows]

    return results

def initialize_db():
    conn = create_db()
    cursor = conn.cursor()
    # Insert Sample Data
    create_unit(cursor, 'ENSC1003', 6)
    create_unit(cursor, 'CITS2401', 6)
    create_unit(cursor, 'MATH1011', 6)
    create_unit(cursor, 'GENG3402', 6)
    create_unit(cursor, 'MATH3023', 6)
    create_unit(cursor, 'MECH3001', 6)
    create_unit(cursor, 'MECH3002', 6)
    create_unit(cursor, 'MECH3024', 6)
    create_unit(cursor, 'MECH3424', 6)
    create_unit(cursor, 'GENG3000', 6)
    create_unit(cursor, 'GENG5010', 6)
    create_unit(cursor, 'GENG5507', 6)
    create_unit(cursor, 'MECH4426', 6)
    create_unit(cursor, 'MECH4502', 6)
    create_unit(cursor, 'MECH5551', 6)
    create_unit(cursor, 'GENG4411', 6)
    create_unit(cursor, 'GENG4412', 6)
    create_unit(cursor, 'MECH5552', 6)
    create_unit(cursor, 'CHPR3405', 6)
    create_unit(cursor, 'GENG5504', 6)
    create_unit(cursor, 'GENG5505', 6)
    create_unit(cursor, 'GENG5514', 6)
    create_unit(cursor, 'MECH4428', 6)
    create_unit(cursor, 'MECH5504', 6)
    create_rule(cursor, 6)
    create_rule(cursor, 18)
    create_rule(cursor, 12)
    create_rule(cursor, 24)
    create_major(cursor,'Computer Science', 2023)
    create_major(cursor,'Computer Science', 2022)

    #Link sample data
    link_unit_rule(cursor,'CITS2401', 1)
    link_unit_rule(cursor,'ENSC1003',2)
    link_unit_rule(cursor,'CITS2401',2)
    link_unit_rule(cursor,'MATH1011',2)
    link_unit_rule(cursor,'CITS2401',3)
    link_unit_rule(cursor,'MATH1011',3)

    link_major_rule(cursor,1,1)
    link_major_rule(cursor,1,3)
    link_major_rule(cursor,1,2)
    link_major_rule(cursor,2,2)
    link_major_rule(cursor,2,3)
    link_major_rule(cursor,2,4)
    link_unit_rule(cursor,'GENG3402', 1)
    link_unit_rule(cursor,'MATH3023', 1)
    link_unit_rule(cursor,'MECH3001', 1)
    link_unit_rule(cursor,'MECH3002', 1)
    link_unit_rule(cursor,'MECH3024', 1)
    link_unit_rule(cursor,'MECH3424', 1)
    link_unit_rule(cursor,'GENG3000', 1)
    link_unit_rule(cursor,'GENG5010', 1)
    link_unit_rule(cursor,'GENG5507', 1)
    link_unit_rule(cursor,'MECH4426', 1)
    link_unit_rule(cursor,'MECH4502', 1)
    link_unit_rule(cursor,'MECH5551', 1)
    link_unit_rule(cursor,'GENG4411', 1)
    link_unit_rule(cursor,'GENG4412', 1)
    link_unit_rule(cursor,'MECH5552', 1)
    link_unit_rule(cursor,'CHPR3405', 1)
    link_unit_rule(cursor,'GENG5504', 1)
    link_unit_rule(cursor,'GENG5505', 1)
    link_unit_rule(cursor,'GENG5514', 1)
    link_unit_rule(cursor,'MECH4428', 1)
    link_unit_rule(cursor,'MECH5504', 1)

    # Commit the changes
    conn.commit()

    return conn

