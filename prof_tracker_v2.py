#%%
import yfinance as yf
import pandas as pd
from collections import defaultdict

def is_year(start, end):
    if length := (end - start) > pd.Timedelta(365, unit='D'): return True

    if length == pd.Timedelta(365, unit='D'):
        if not start.is_leap_year(): return True

    return False

movement = pd.read_excel('C:\\Users\\decoy\\Documents\\Finance\\transactions.xlsx', sheet_name='Movement')
dividend = pd.read_excel('C:\\Users\\decoy\\Documents\\Finance\\transactions.xlsx', sheet_name='Dividend')
cash = pd.read_excel('C:\\Users\\decoy\\Documents\\Finance\\transactions.xlsx', sheet_name='Cash')
movement['Cost'] = [movement['Price'][idx] - movement['Fees'][idx] / movement['Quantity'][idx] if i == 'Sell' else movement['Price'][idx] + movement['Fees'][idx] / movement['Quantity'][idx] for idx, i in enumerate(movement['Action'])]
# print(movement)


sells = movement[movement['Action'] == 'Sell']
sells.reset_index(drop=True, inplace=True)
buys = movement[movement['Action'] == 'Buy'][::-1]
buys.reset_index(drop=True, inplace=True)

closed_profits = pd.DataFrame(columns=['Date', 'Code', 'Profit', 'Profit (%)', 'Type'])
open_profits = pd.DataFrame(columns=['Code', 'Quantity', 'Amount'])
tax = pd.DataFrame(columns=['Date', 'Code', 'Amount'])

for b_index, b_row in buys.iterrows():
    b_date, b_code, b_quantity, b_action, b_price, b_fees, b_exchange, b_cost = b_row

    for s_index, s_row in sells.loc[(sells['Date'] >= b_date) & (sells['Code'] == b_code)].iterrows():
        s_date, s_code, s_quantity, s_action, s_price, s_fees, s_exchange, s_cost = s_row
        

        if s_quantity <= b_quantity:
            profit = s_quantity * (s_cost * s_exchange - b_cost * b_exchange)
            profit_p = 100 * (s_cost * s_exchange - b_cost * b_exchange)/(b_cost * b_exchange)
            new_row = {'Date': s_date, 'Code': b_code, 'Profit': profit, 'Profit (%)': profit_p, 'Type': 'Capital Gains'}
            closed_profits = closed_profits.append(new_row, ignore_index=True)

            discount = 0.5 if is_year(b_date, s_date) else 1
            t_row = {'Date':s_date, 'Code': s_code, 'Amount': profit * discount} if profit > 0 else {'Date':s_date, 'Code': s_code, 'Amount': profit}
            tax = tax.append(t_row, ignore_index=True)
                
            b_quantity -= s_quantity
            sells = sells.drop(s_index)


        elif s_quantity > b_quantity:
            profit = b_quantity * (s_cost * s_exchange - b_cost * b_exchange)
            profit_p = 100 * (s_cost * s_exchange - b_cost * b_exchange)/(b_cost * b_exchange)
            new_row = {'Date': s_date, 'Code': b_code, 'Profit': profit, 'Profit (%)': profit_p, 'Type': 'Capital Gains'}
            closed_profits = closed_profits.append(new_row, ignore_index=True)

            discount = 0.5 if is_year(b_date, s_date) else 1
            t_row = {'Date':s_date, 'Code': s_code, 'Amount': profit * discount} if profit > 0 else {'Date':s_date, 'Code': s_code, 'Amount': profit}
            tax = tax.append(t_row, ignore_index=True)

            sells.at[s_index, 'Quantity'] -= b_quantity
            b_quantity = 0

        if b_quantity == 0: break
# print(closed_profits)
for d_index, d_row in dividend.iterrows():
    d_date, d_code, d_amount, d_frank = d_row
    new_row = {'Date': d_date, 'Code': d_code, 'Profit': d_amount + d_frank , 'Profit (%)': 'N/A', 'Type': 'Dividend'}
    closed_profits = closed_profits.append(new_row, ignore_index=True)
    t_row = {'Date':d_date, 'Code': d_code, 'Amount': (d_amount + d_frank) + (d_amount + d_frank) * 0.19 - d_frank}
    tax = tax.append(t_row, ignore_index=True)


close_profits_sum = closed_profits.groupby('Code', sort = False)['Profit'].sum().reset_index()
tax_sum = tax.groupby('Code', sort = False)['Amount'].sum().reset_index()
print(close_profits_sum )
# print(tax_sum)
print(f'The total amount of closed profit is ${close_profits_sum["Profit"].sum()}')

print(f'The amount to be added to your income is ${tax_sum["Amount"].sum()}')
