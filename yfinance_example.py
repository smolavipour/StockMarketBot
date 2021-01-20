import datetime as dt
import yfinance as yf
import pandas as pd



stocks=['AMZN','MSFT']

start = dt.datetime.today() - dt.timedelta(30)

end = dt.datetime.today()

cl_Price = pd.DataFrame()

for ticker in stocks:
    cl_Price[ticker] = yf.download(ticker, start, end)['Adj Close']
    
    