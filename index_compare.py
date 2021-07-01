import yfinance as yf
import pandas as pd

movement = pd.read_excel('C:\\Users\\decoy\\Documents\\Finance\\transactions.xlsx', sheet_name='Movement')
dividend = pd.read_excel('C:\\Users\\decoy\\Documents\\Finance\\transactions.xlsx', sheet_name='Dividend')
cash = pd.read_excel('C:\\Users\\decoy\\Documents\\Finance\\transactions.xlsx', sheet_name='Cash')
exchange = pd.read_excel('C:\\Users\\decoy\\Documents\\Finance\\transactions.xlsx', sheet_name='Exchange')
movement['Cost'] = [movement['Price'][idx] - movement['Fees'][idx] / movement['Quantity'][idx] if i == 'Sell' else movement['Price'][idx] + movement['Fees'][idx] / movement['Quantity'][idx] for idx, i in enumerate(movement['Action'])]

sec_set = list(set(movement['Code'].tolist()))
sec_set.sort()
main = pd.DataFrame(index=sec_set)

open_code = ' '.join(sec_set)
data = yf.download(open_code, start=cash['Date'][0] + pd.Timedelta(1, unit='D'), group_by='ticker')
data.fillna(method='bfill', inplace=True)

col = dict.fromkeys(sec_set, 0)
main[cash.loc[0, 'Date']] = main.index.map(col)

for idx, row in movement.iterrows():
    date, code, quantity, action, price, fees, exchange, cost = row
    col = main.iloc[:, -1].to_dict()
    col[code] += quantity if action == 'Buy' else -quantity
    main[date] = main.index.map(col)

main_days = movement['Date'].tolist()
main_days.insert(0, cash.loc[0, 'Date'])
days = list(data.index.values)
c_value = 0
next_change = 1
for day in days:
    try:
        cashloc = cash[cash['Date'] == day]
        cashflow = cashloc['Credit'].sum() - cashloc['Debit'].sum()
    except:
        cashflow = 0
    
    try:
        divloc = dividend[dividend['Date'] == day]
        div = divloc['Amount'].sum() + divloc['Franking Credit'].sum()
    except:
        div = 0

    c_value += cashflow + div

    value = 0
    next = main_days[next_change]
    last = main_days[next_change - 1]
    if day < next:
        value += sum([data[code]['Close'][str(day.date())] * x if (x := main.loc[code, last]) != 0 else 0 for code in sec_set])

    elif day == next:
        c_value += movement.loc[next_change - 1, 'Cost'] * movement.loc[next_change - 1, 'Quantity'] if movement.loc[next_change - 1, 'Action'] == 'Sell' else -movement.loc[next_change - 1, 'Cost'] * movement.loc[next_change - 1, 'Quantity']
        value += sum([data[code]['Close'][str(day.date())] * x if (x := main.loc[code, next]) != 0 else 0 for code in sec_set])
        next_change += 1
    print(day.date())
    print(value, c_value, value + c_value)
    print('')