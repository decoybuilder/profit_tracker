# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
import pandas as pd


# %%
movement = pd.read_excel('C:\\Users\\decoy\\Documents\\Finance\\transactions.xlsx', sheet_name='Movement')
dividend = pd.read_excel('C:\\Users\\decoy\\Documents\\Finance\\transactions.xlsx', sheet_name='Dividend')
cash = pd.read_excel('C:\\Users\\decoy\\Documents\\Finance\\transactions.xlsx', sheet_name='Cash')


# %%
sells = movement[movement['Action'] == 'Sell']
sells.reset_index(drop=True, inplace=True)
buys = movement[movement['Action'] == 'Buy']
buys.reset_index(drop=True, inplace=True)


# %%
closed_profits_dict = {}
while len(sells) != 0:
    sells.reset_index(drop=True, inplace=True)
    buys.reset_index(drop=True, inplace=True)
    sell_index = len(sells) - 1
    s_date, s_code, s_quantity, s_action, s_price, s_fees = sells.loc[sell_index]

    for buy_index in range(len(buys) - 1, -1, -1):
        if (s_code == buys.loc[buy_index]['Code']) and (sells.loc[sell_index]['Date'] >= buys.loc[buy_index]['Date']):
            b_date, b_code, b_quantity, b_action, b_price, b_fees = buys.loc[buy_index]

            name = b_code.replace('.', '_').lower()
            if name not in closed_profits_dict:
                closed_profits_dict[name] = 0
            
            if s_quantity < b_quantity:
                closed_profits_dict[name] += s_price * s_quantity - b_price * s_quantity - s_fees
                buys.at[buy_index, 'Quantity'] -= s_quantity
                sells.drop(sells.index[-1], inplace=True)
                break
            
            elif s_quantity == b_quantity:
                closed_profits_dict[name] += s_price * s_quantity - b_price *   b_quantity - s_fees - b_fees
                buys.drop([buy_index], inplace=True)
                sells.drop(sells.index[-1], inplace=True)
                break

            else:
                closed_profits_dict[name] += s_price * b_quantity - b_price *   b_quantity - s_fees - b_fees
                sells.at[sell_index, 'Quantity'] -= b_quantity
                buys.drop([buy_index], inplace=True)
                break


# %%
for div_index in range(0, len(dividend)):
    d_date, d_code, d_amount  = dividend.loc[div_index]
    name = d_code.replace('.', '_').lower()

    if name not in closed_profits_dict:
        closed_profits_dict[name] = 0
        
    closed_profits_dict[name] += d_amount


# %%
cash_tot = sum(cash['Credit']) - sum(cash['Debit'])


# %%
closed_profits = sum(closed_profits_dict.values())
print(closed_profits_dict)
print(closed_profits)


# %%



