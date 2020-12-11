import asx_data
import time
import sqlite3
import pandas as pd
import concurrent.futures
import database_func
import math

list = pd.read_csv('test.csv')

conn = sqlite3.connect('asx_data.db')
c = conn.cursor()


start = time.perf_counter()

results = []
while True:
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = [executor.submit(asx_data.basic_d, code) for code in list['Code']]

        for f in concurrent.futures.as_completed(results):
            code, price, volume = f.result()

            if math.isnan(price):
                continue
    
            l_code, l_price, l_volume = database_func.get_last_values(code)
            
            if volume > l_volume:
                print(code, price, volume)
                database_func.insert_std(code, round(time.time()), price, volume)


    finish = time.perf_counter()

    print(finish - start)