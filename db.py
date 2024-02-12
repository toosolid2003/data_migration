import sqlite3
# import pydantic

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn

def create_item(conn, item):
    """
    Creates a new item in the db
    item: Item
    conn: Connection object
    """
    data = item.model_dump()    #converts items to dict
    data = tuple(data.values()) #converts dict to tuple

    sql = ''' INSERT INTO items(ind, organization, name, website, country, description, founded, industry, employees)
    VALUES(?,?,?,?,?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, data)
    conn.commit()