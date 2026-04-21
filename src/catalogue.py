import httpx
import asyncio
import os
import sqlite3

def populate_db():
    print("STARTING DB")

    url = "https://demo.trading212.com/api/v0/equity/metadata/instruments"
    token = os.getenv("T212_CREDS_DEMO")
    instruments = []

# Fetch all instruments from T212

    with httpx.Client() as client:
        if not token:
            print('Error: Aut Token invalid or missing')
        else:
            headers = {'Authorization': f'Basic {token}'}
            r = client.get(url, headers=headers)
            instruments = r.json()
            if r.status_code == 429:
                print("Stop spamming me")

# We only need STOCKS, their name and T212 ticker symbol
    stocks = [
        {"name": item.get("name").lower(),
        "ticker": item.get("ticker")
        }
        for item in instruments
        if item.get("type") == "STOCK"
    ]

# Store that info in a SQLite DB (Shout Out SQLite)
# The way it works is a little new to me:
#
# First we create a connection to the db (setup_db.py)
# this will create a database if one doesnt exist already.
#
# Then we create a cursor which is used to create a table, add entries, write queries and acts
# like a window on the returned result set to allow us to read the returned data.
#
# To commit our changes we have to use the .commit() function.
#
# Finally once our script is complete we have to close the connection

    connection = sqlite3.connect("stocks.db")
    cursor = connection.cursor()

# Clear the table
    cursor.execute("DELETE FROM stocks")

# Insert data, mapping the "company_name" & "company_ticker" DB fields
# to the stocks object "name" and "ticker" keys.

    cursor.executemany("INSERT INTO stocks (company_name, company_ticker) VALUES (:name, :ticker)", stocks)

    connection.commit()

    res = cursor.execute("SELECT company_name, company_ticker FROM stocks WHERE company_name = 'nvidia'")
    row = res.fetchall()
    print(row)

# close the connection

    connection.close()


if __name__ == '__main__':
    populate_db()
