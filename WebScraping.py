import requests
from bs4 import BeautifulSoup
import pandas as pd


Financial_dir = {}
Tickers = ['AAPL', 'MSFT']
for ticker in Tickers:
    Data_dir={}
    url = 'https://finance.yahoo.com/quote/'+ticker+'?p='+ticker+'&.tsrc=fin-srch'
    page = requests.get(url)
    page_content = page.content
    soup = BeautifulSoup(page_content,'html.parser')
    table = soup.find_all("table",{"class":"W(100%)"})
    
    for t in table:
        rows = t.find_all("tr")
        for row in rows:
            Data_dir[row.get_text(separator='|').split('|')[0]] = row.get_text(separator='|').split('|')[1]
    Financial_dir[ticker] = Data_dir
Combined_data = pd.DataFrame(Financial_dir)