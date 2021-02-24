import requests
from bs4 import BeautifulSoup
import pandas as pd


input_data_path = 'myTickerList.txt'
Tickers = pd.read_csv(input_data_path, header=None, names=['tk'])


#Tickers = ['AAPL', 'MSFT']
premarket = pd.DataFrame(columns=['Ticker','Change (pre)'])
aftermarket = pd.DataFrame(columns=['Ticker','Change (after)'])



for ticker in Tickers.tk:
    Data_dir={}
    url = 'https://www.marketwatch.com/investing/stock/'+ticker
    page = requests.get(url)
    page_content = page.content
    soup = BeautifulSoup(page_content,'html.parser')
    if soup.select("span.change--percent--q>bg-quote")[0].get('session') == 'pre':
        #Premarket
        pre_market_change = soup.select("span.change--percent--q>bg-quote")[0].get_text()
        #print(pre_market_change)
        premarket = premarket.append({'Ticker':ticker, 'Change (pre)':pre_market_change}, ignore_index=True)
    elif soup.select("span.change--percent--q>bg-quote")[0].get('session') == 'after':
        #Aftermarket
        after_market_change = soup.select("span.change--percent--q>bg-quote")[0].get_text()
        #print(pre_market_change)
        aftermarket = aftermarket.append({'Ticker':ticker, 'Change (after)':after_market_change}, ignore_index=True)        

if soup.select("span.change--percent--q>bg-quote")[0].get('session') == 'pre':
    display(premarket)
elif soup.select("span.change--percent--q>bg-quote")[0].get('session') == 'after':
    display(aftermarket)