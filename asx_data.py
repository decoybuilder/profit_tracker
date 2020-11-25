from bs4 import BeautifulSoup
import requests

# source = requests.get('https://www.asx.com.au/asx/1/share/nab/').text

# soup = BeautifulSoup(source, 'lxml')

# data = soup.p.text

# last_price_loc = data.find('last_price')
# start = data.find(':', last_price_loc) + 1
# end = data.find(',', start)
# print(start, end)

# print(data[start:end])

def last_price(code):
    address = 'https://www.asx.com.au/asx/1/share/' + code + '/'
    source = requests.get(address).text
    soup = BeautifulSoup(source, 'lxml')

    data = soup.p.text

    last_price_loc = data.find('last_price')
    start = data.find(':', last_price_loc) + 1
    end = data.find(',', start)
    
    return data[start:end]

print(type(float(last_price('nab'))))