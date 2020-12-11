import sqlite3

conn = sqlite3.connect('asx_data.db')
c = conn.cursor()

def insert_std(code, time, price, volume):
    with conn:
        name = 'asx_' + code
        c.execute("INSERT INTO '{}' VALUES (:time, :price, :volume)".format(name), {'time': time, 'price': price, 'volume': volume})


def get_last_values(code):
    name = 'asx_' + code
    c.execute("""SELECT * FROM '{}' ORDER BY volume DESC LIMIT 1""".format(name))
    
    return c.fetchone()