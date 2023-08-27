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
        FOREIGN KEY(unit_code) REFERENCES Units(unit_code),
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


conn = create_db()
cursor = conn.cursor()
# Insert Sample Data
cursor.execute("INSERT INTO Units(unit_code, credit_pts) VALUES('CITS2401', 6);")
cursor.execute("INSERT INTO Units(unit_code, credit_pts) VALUES('ENSC1003', 6);")
cursor.execute("INSERT INTO Groups(name) VALUES('Group A');")
cursor.execute("INSERT INTO Groups(name) VALUES('Group B');")
cursor.execute("INSERT INTO Rules(value) VALUES(6);")
cursor.execute("INSERT INTO Rules(value) VALUES(18);")
cursor.execute("INSERT INTO RuleUnits(unit_code, rule_id) VALUES('CITS2401', 1);")
cursor.execute("INSERT INTO RuleUnits(unit_code, rule_id) VALUES('ENSC1003', 2);")
cursor.execute("INSERT INTO RuleUnits(unit_code, rule_id) VALUES('CITS2401', 2);")
cursor.execute("INSERT INTO Major(name, year) VALUES('Computer Science', 2023);")
cursor.execute("INSERT INTO MajorRules(major_id, rule_id) VALUES(1, 1);")
cursor.execute("INSERT INTO MajorRules(major_id, rule_id) VALUES(1, 2);")

# Commit the changes
conn.commit()

#Test getting the rules for sample data
rules = select_all_rules(conn, 'Computer Science', 2023)


print(rules)