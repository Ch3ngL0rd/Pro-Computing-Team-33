import sqlite3

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except sqlite3.Error as e:
        print(e)

    return conn

def select_all_rules(conn, major, yr):
    """
    Query all rows in the Rules table to get all rules for a given degree
    """
    cursor = conn.cursor()
# Query to retrieve the desired information
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
        rule_value, unit_codes = row
        unit_codes_list = unit_codes.split(',')  # Split the comma-separated unit codes
        output.append((rule_value, unit_codes_list))

    # Close the connection
    conn.close()

    return output