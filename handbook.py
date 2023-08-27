import sqlite3

# Connect to an in-memory SQLite database
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
CREATE TABLE GroupUnits (
    unit_code TEXT,
    group_id INTEGER,
    FOREIGN KEY(unit_code) REFERENCES Units(unit_code),
    FOREIGN KEY(group_id) REFERENCES Groups(group_id),
    PRIMARY KEY(unit_code, group_id)
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

# Insert Sample Data
cursor.execute("INSERT INTO Units(unit_code, credit_pts) VALUES('CITS2401', 6);")
cursor.execute("INSERT INTO Units(unit_code, credit_pts) VALUES('ENSC1003', 6);")
cursor.execute("INSERT INTO Groups(name) VALUES('Group A');")
cursor.execute("INSERT INTO Groups(name) VALUES('Group B');")
cursor.execute("INSERT INTO GroupUnits(unit_code, group_id) VALUES('CITS2401', 1);")
cursor.execute("INSERT INTO GroupUnits(unit_code, group_id) VALUES('ENSC1003', 2);")
cursor.execute("INSERT INTO Rules(value) VALUES(6);")
cursor.execute("INSERT INTO Rules(value) VALUES(18);")
cursor.execute("INSERT INTO Major(name, year) VALUES('Computer Science', 2023);")
cursor.execute("INSERT INTO MajorRules(major_id, rule_id) VALUES(1, 1);")
cursor.execute("INSERT INTO MajorRules(major_id, rule_id) VALUES(1, 2);")

# Commit the changes
conn.commit()

# Prints the database
cursor.execute("SELECT * FROM Units;")
print("Units")
print(cursor.fetchall())
cursor.execute("SELECT * FROM Groups;")
print("Groups")
print(cursor.fetchall())
cursor.execute("SELECT * FROM GroupUnits;")
print("GroupUnits")
print(cursor.fetchall())
cursor.execute("SELECT * FROM Rules;")
print("Rules")
print(cursor.fetchall())
cursor.execute("SELECT * FROM Major;")
print("Major")
print(cursor.fetchall())
cursor.execute("SELECT * FROM MajorRules;")
print("MajorRules")
print(cursor.fetchall())