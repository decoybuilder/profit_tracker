import asx_data
import pandas as pd

print(len(asx_data.get_eod('nab', 10000)))