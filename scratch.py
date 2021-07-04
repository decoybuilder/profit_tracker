import cProfile
import pstats

with cProfile.Profile() as pr:
    import yfinance as yf
    import pandas as pd

    def is_year(start, end):
        if length := (end - start) > pd.Timedelta(365, unit='D'): return True

        if length == pd.Timedelta(365, unit='D'):
            if not start.is_leap_year(): return True

        return False

    movement = pd.read_excel('C:\\Users\\decoy\\Documents\\Finance\\transactions.xlsx', sheet_name='Movement')
    dividend = pd.read_excel('C:\\Users\\decoy\\Documents\\Finance\\transactions.xlsx', sheet_name='Dividend')
    cash = pd.read_excel('C:\\Users\\decoy\\Documents\\Finance\\transactions.xlsx', sheet_name='Cash')
    exchange = pd.read_excel('C:\\Users\\decoy\\Documents\\Finance\\transactions.xlsx', sheet_name='Exchange')
    movement['Cost'] = [movement['Price'][idx] - movement['Fees'][idx] / movement['Quantity'][idx] if i == 'Sell' else movement['Price'][idx] + movement['Fees'][idx] / movement['Quantity'][idx] for idx, i in enumerate(movement['Action'])]


    sells = movement[movement['Action'] == 'Sell']
    sells.reset_index(drop=True, inplace=True)
    buys = movement[movement['Action'] == 'Buy'][::-1]
    buys.reset_index(drop=True, inplace=True)

    closed_profits = pd.DataFrame(columns=['Date', 'Code', 'Profit', 'Profit (%)', 'Type'])
    open_profits = pd.DataFrame(columns=['Code', 'Quantity', 'Cost'])
    tax = pd.DataFrame(columns=['Date', 'Code', 'Amount'])

    for b_index, b_row in buys.iterrows():
        b_date, b_code, b_quantity, b_action, b_price, b_fees, b_exchange, b_cost = b_row

        for s_index, s_row in sells.loc[(sells['Date'] >= b_date) & (sells['Code'] == b_code)].iterrows():
            s_date, s_code, s_quantity, s_action, s_price, s_fees, s_exchange, s_cost = s_row
            

            if s_quantity <= b_quantity:
                profit = s_quantity * (s_cost / s_exchange - b_cost/ b_exchange)
                profit_p = 100 * (s_cost / s_exchange - b_cost / b_exchange)/(b_cost / b_exchange)
                new_row = {'Date': s_date, 'Code': b_code, 'Profit': profit, 'Profit (%)': profit_p, 'Type': 'Capital Gains'}
                closed_profits = closed_profits.append(new_row, ignore_index=True)

                discount = 0.5 if is_year(b_date, s_date) else 1
                t_row = {'Date':s_date, 'Code': s_code, 'Amount': profit * discount} if profit > 0 else {'Date':s_date, 'Code': s_code, 'Amount': profit}
                tax = tax.append(t_row, ignore_index=True)
                    
                b_quantity -= s_quantity
                sells = sells.drop(s_index)


            elif s_quantity > b_quantity:
                profit = b_quantity * (s_cost / s_exchange - b_cost / b_exchange)
                profit_p = 100 * (s_cost / s_exchange - b_cost / b_exchange)/(b_cost / b_exchange)
                new_row = {'Date': s_date, 'Code': b_code, 'Profit': profit, 'Profit (%)': profit_p, 'Type': 'Capital Gains'}
                closed_profits = closed_profits.append(new_row, ignore_index=True)

                discount = 0.5 if is_year(b_date, s_date) else 1
                t_row = {'Date':s_date, 'Code': s_code, 'Amount': profit * discount} if profit > 0 else {'Date':s_date, 'Code': s_code, 'Amount': profit}
                tax = tax.append(t_row, ignore_index=True)

                sells.at[s_index, 'Quantity'] -= b_quantity
                b_quantity = 0

            if b_quantity == 0: break

        if b_quantity != 0:
            o_row = {'Code': b_code, 'Quantity': b_quantity, 'Cost': b_cost / b_exchange}
            open_profits = open_profits.append(o_row, ignore_index=True)

    for d_index, d_row in dividend.iterrows():
        d_date, d_code, d_amount, d_frank = d_row
        new_row = {'Date': d_date, 'Code': d_code, 'Profit': d_amount + d_frank , 'Profit (%)': 'N/A', 'Type': 'Dividend'}
        closed_profits = closed_profits.append(new_row, ignore_index=True)
        t_row = {'Date':d_date, 'Code': d_code, 'Amount': (d_amount + d_frank) + (d_amount + d_frank) * 0.19 - d_frank}
        tax = tax.append(t_row, ignore_index=True)


    close_profits_sum = closed_profits.groupby('Code', sort = False)['Profit'].sum().reset_index()
    tax_sum = tax.groupby('Code', sort = False)['Amount'].sum().reset_index()

    open_profits['Cost Base'] = open_profits['Cost'] * open_profits['Quantity']
    open_profits_sum = open_profits.groupby('Code', sort = False)['Quantity'].sum().reset_index()
    open_profits_sum = open_profits_sum.merge(open_profits.groupby('Code', sort = False)['Cost Base'].sum().reset_index(), on='Code')
    open_profits_sum['Avg Cost'] = open_profits_sum['Cost Base'] / open_profits_sum['Quantity']

    open_code = '^AXJO ' + ' '.join(open_profits_sum['Code'].tolist())

    data = yf.download(open_code, start=cash['Date'][0].date(), group_by='ticker')

    # open_profits_sum['Market Price'] = [x if not pd.isna(x := data[i]['Close'][-1]) else data[i]['Close'][-2] for i in open_profits_sum['Code']]
    market_list = [0] * len(open_profits_sum['Code'])
    cache = {'AX':1}
    for idx, code in enumerate(open_profits_sum['Code']):
        code_split = code.split('.')
        if len(code_split) == 1: code_split.append('USA')
            
        cur = code_split[1]
        try:
            rate = cache[cur]

        except:
            ex_code = exchange.loc[exchange['Suffix'] == cur]['Code'].reset_index(drop=True)[0]
            rate = yf.Ticker(ex_code).history(period='1d')['Close'][0]
            cache[cur] = rate

        market_list[idx] = x / rate if not pd.isna(x := data[code]['Close'][-1]) else data[code]['Close'][-2] / rate


    open_profits_sum['Market Price'] = market_list
    open_profits_sum['Profit'] = (open_profits_sum['Market Price'] - open_profits_sum['Avg Cost']) * open_profits_sum['Quantity']
    open_profits_sum['Profit (%)'] = 100 * (open_profits_sum['Market Price'] - open_profits_sum['Avg Cost']) / open_profits_sum['Avg Cost']


    print('Closed Profits')
    print(close_profits_sum )
    print(f'The total amount of closed profit is ${close_profits_sum["Profit"].sum()}')
    print(f'The amount to be added to your income is ${tax_sum["Amount"].sum()}')
    print('\n')
    print('Unclosed Profits')
    print(open_profits_sum)
    print(f'The total amount of open profit is ${open_profits_sum["Profit"].sum()}')

stats = pstats.Stats(pr)
stats.sort_stats(pstats.SortKey.TIME)
stats.print_stats()
