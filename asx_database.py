import sqlite3
import time
import pandas as pd
import asx_data
import database_func

list = pd.read_csv('test.csv')

conn = sqlite3.connect('asx_data.db')
c = conn.cursor()

for code in list['Code']:
    name = 'asx_' + code
    c.execute("""CREATE TABLE '{}' (
                time integer,
                price real,
                volume integer
                )""".format(name))

conn.commit()

conn.close()

# code, price, volume = asx_data.basic_d('NAB')

# # database_func.insert_std(code, round(time.time()), price, volume)
# print(database_func.get_last_price('NAB'))