import yfinance as yf
import pandas as pd
from matplotlib import pyplot as plt

movement = pd.read_excel('C:\\Users\\decoy\\Documents\\Finance\\transactions.xlsx', sheet_name='Movement')
dividend = pd.read_excel('C:\\Users\\decoy\\Documents\\Finance\\transactions.xlsx', sheet_name='Dividend')
cash = pd.read_excel('C:\\Users\\decoy\\Documents\\Finance\\transactions.xlsx', sheet_name='Cash')
exchange = pd.read_excel('C:\\Users\\decoy\\Documents\\Finance\\transactions.xlsx', sheet_name='Exchange')
movement['Cost'] = [movement['Price'][idx] - movement['Fees'][idx] / movement['Quantity'][idx] if i == 'Sell' else movement['Price'][idx] + movement['Fees'][idx] / movement['Quantity'][idx] for idx, i in enumerate(movement['Action'])]

sec_set = list(set(movement['Code'].tolist()))
sec_set.sort()
main = pd.DataFrame(index=sec_set)

open_code = '^AXJO ' + ' '.join(sec_set)
data = yf.download(open_code, start=cash['Date'][0] + pd.Timedelta(1, unit='D'), group_by='ticker')
data.fillna(method='bfill', inplace=True)
data.fillna(0, inplace=True)
data.replace(to_replace=0, method='ffill', inplace=True)

col = dict.fromkeys(sec_set, 0)
main[cash.loc[0, 'Date']] = main.index.map(col)

for idx, row in movement.iterrows():
    date, code, quantity, action, price, fees, m_exchange, cost = row
    col = main.iloc[:, -1].to_dict()
    col[code] += quantity if action == 'Buy' else -quantity
    main[date] = main.index.map(col)

main_days = movement['Date'].tolist()
main_days = list(dict.fromkeys(main_days))
main_days.insert(0, cash.loc[0, 'Date'])
main_days.append(pd.Timestamp('today') + pd.Timedelta(days=1))

days = list(data.index.values)
c_value = 0
div_value = 0
inflows = 0 
next_change = 1
port_val = []
index_shares = 0
index_val = []
port_return = []
index_return = []
index_lad_returns = []
port_lad_returns = []
index_lad_returns_cum = []
port_lad_returns_cum = []
cache = {'AX':1}
for day in days:
    try:
        cashloc = cash[cash['Date'] == day]
        cashflow = cashloc['Credit'].sum() - cashloc['Debit'].sum()

        inflows += cashflow
        index_shares += cashflow / data['^AXJO']['Close'][str(day.date())]
    except:
        cashflow = 0
    

    try:
        divloc = dividend[dividend['Date'] == day]
        div = divloc['Amount'].sum() + divloc['Franking Credit'].sum()
    except:
        div = 0

    div_value += div
    c_value += cashflow + div

    value = 0

    next = main_days[next_change]
    # try:
    #     next = main_days[next_change]
    # except:
    #     next = main_days[next_change - 1]

    last = main_days[next_change - 1]
    if day < next:
        # value += sum([data[code]['Close'][str(day.date())] * x if (x := main.loc[code, last]) != 0 else 0 for code in sec_set])
        for code in sec_set:
            if (x := main.loc[code, last]) != 0:
                code_split = code.split('.')
                if len(code_split) == 1: code_split.append('USA')
                    
                cur = code_split[1]
                try:
                    rate = cache[cur]

                except:
                    ex_code = exchange.loc[exchange['Suffix'] == cur]['Code'].reset_index(drop=True)[0]
                    rate = yf.Ticker(ex_code).history(period='1d')['Close'][0]
                    cache[cur] = rate

                value += data[code]['Close'][str(day.date())] * x / rate

    elif day == next:
        for idx, row in movement[movement['Date'] == day].iterrows():
            t_date, t_code, t_quantity, t_action, t_price, t_fees, t_exchange, t_cost = row
            c_value += t_cost * t_quantity if t_action == 'Sell' else -t_cost * t_quantity

        # value += sum([data[code]['Close'][str(day.date())] * x if (x := main.loc[code, next]) != 0 else 0 for code in sec_set])
        for code in sec_set:
            if (x := main.loc[code, next]) != 0:
                code_split = code.split('.')
                if len(code_split) == 1: code_split.append('USA')
                    
                cur = code_split[1]
                try:
                    rate = cache[cur]

                except:
                    ex_code = exchange.loc[exchange['Suffix'] == cur]['Code'].reset_index(drop=True)[0]
                    rate = yf.Ticker(ex_code).history(period='1d')['Close'][0]
                    cache[cur] = rate

                value += data[code]['Close'][str(day.date())] * x / rate
        next_change += 1
    # print(day.date())
    # print(value, c_value, value + c_value, inflows)
    # print('')

    port_val.append(value + c_value)
    port_multiplier = (value + c_value)/inflows
    port_return.append((port_multiplier - 1) * 100)
    index = index_shares *  data['^AXJO']['Close'][str(day.date())]
    index_val.append(index)
    index_multiplier = index/inflows
    index_return.append((index_multiplier - 1)  * 100)
    
    if len(port_lad_returns) == 0:
        port_lad_returns.append((port_multiplier - 1) * 100)
        index_lad_returns.append((index_multiplier - 1) * 100)

        port_lad_returns_cum.append((port_multiplier - 1) * 100)
        index_lad_returns_cum.append((index_multiplier - 1) * 100)
    else:
        temp_port = (port_val[-1] - port_val[-2] - cashflow)/inflows
        port_lad_returns.append(temp_port * 100)

        temp_index = (index_val[-1] - index_val[-2] - cashflow)/inflows
        index_lad_returns.append(temp_index * 100)

        port_lad_returns_cum.append(((port_lad_returns_cum[-1]/100 + 1) * (1 + temp_port) - 1) * 100)
        index_lad_returns_cum.append(((index_lad_returns_cum[-1]/100 + 1) * (1 + temp_index) - 1) * 100)

plt.figure(0)
plt.plot(days, port_val)
plt.plot(days, index_val)

plt.figure(1)
plt.plot(days, port_return)
plt.plot(days, index_return)
plt.legend(['Your Portfolio', 'ASX 200'])

plt.figure(2)
plt.plot(days, port_lad_returns)
plt.plot(days, index_lad_returns)
plt.legend(['Your Portfolio', 'ASX 200'])
plt.title('Lad Returns')

plt.figure(3)
plt.plot(days, port_lad_returns_cum)
plt.plot(days, index_lad_returns_cum)
plt.legend(['Your Portfolio', 'ASX 200'])
plt.title('Lad Returns Cum')
plt.show()