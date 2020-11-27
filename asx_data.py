from bs4 import BeautifulSoup
import requests

def last_price(code):
    address = 'https://www.asx.com.au/asx/1/share/' + code + '/'
    source = requests.get(address).text
    soup = BeautifulSoup(source, 'lxml')

    data = soup.p.text

    last_price_loc = data.find('last_price')
    start = data.find(':', last_price_loc) + 1
    end = data.find(',', start)
    
    return float(data[start:end])
