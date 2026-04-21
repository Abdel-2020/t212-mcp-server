import sqlite3

# Store that info in a SQLite DB (Shout Out SQLite)
# The way it works is a little new to me:
# First we create a connection to the db (setup_db.py)
#   this will create a database if one doesnt exist already.
# Then we create a cursor which is used to create a table, add entries, write queries and acts
#   like a window on the returned result set to allow us to read the returned data.
# Finally once our script is complete we have to close the connection

connection = sqlite3.connect("stocks.db")
cursor = connection.cursor()


cursor.execute("""
    CREATE TABLE stocks(
        id INTEGER PRIMARY KEY,
        company_name TEXT NOT NULL,
        company_ticker TEXT NOT NULL
        ) STRICT;
    """)

connection.close()
