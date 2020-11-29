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

def basic(code):
    address = 'https://www.asx.com.au/asx/1/share/' + code + '/'
    source = requests.get(address).text
    soup = BeautifulSoup(source, 'lxml')

    data = soup.p.text

    last_price_loc = data.find('last_price')
    
    if last_price_loc == -1:
        return float('nan'), float('nan')

    start = data.find(':', last_price_loc) + 1
    end = data.find(',', start)

    last_price = float(data[start:end])

    volume_loc = data.find('volume')
    start = data.find(':', volume_loc) + 1
    end = data.find(',', start)
    volume = int(data[start:end])

    return last_price, volume