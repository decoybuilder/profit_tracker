import yfinance as yf
import pandas as pd

test = yf.Ticker('AUDUSD=X')

# a = test.history(period='1d')

# print(a)

# data = yf.download(" ^AORD AVUV", start="2021-01-01", group_by='Currency')
# print(data)
# print(pd.isna(data['AVUV']['Close'][-1]))



# data = yf.download("NAB.AX CBA.AX STW.AX FLT.AX", period='1d',
#                    group_by="ticker")

# print(data['CBA.AX']['Close'])


# b = yf.Ticker('AIR.DE')
# print(b.info['currency'])

# c = 'AVUV.AX'
# print(c.split('.'))

# a = pd.DataFrame(columns=['Date', 'Code', 'Profit', 'Profit (%)', 'Type'])
# a['test'][0] = 1
# a = [0] * 10
# print(yf.Ticker('AUDUSD=X').history(period='1d')['Close'][0])


# arrays = [np.array(["bar", "bar", "baz", "baz", "foo", "foo", "qux", "qux"]), np.array(["one", "two", "one", "two", "one", "two", "one", "two"])]
# s = pd.Series(np.random.randn(8), index=arrays)
# df = pd.DataFrame(np.random.randn(8, 4), index=arrays)
# print(df)

# writer = pd.ExcelWriter('testData.xlsx')
# df.to_excel(writer, 'Sheet1')
# writer.save()


data = [1, 0, 0, 2, 0, 4, 6, 8, 0, 0, 0, 0, 2, 1]
df = pd.DataFrame(data=data, columns = ['A'])

print(df.replace(to_replace=0, method='ffill'))