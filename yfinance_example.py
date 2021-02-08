import datetime as dt
import yfinance as yf
import pandas as pd



stocks=['ADMP']

#start = dt.datetime.today() - dt.timedelta(30)

#end = dt.datetime.today()

start = '2021-01-27'
end = '2021-01-27'

cl_Price = pd.DataFrame()


for ticker in stocks:
    cl_Price[ticker] = yf.download(ticker, start, end)['Adj Close']
    day_technicals = yf.Ticker(ticker).history(start=start, end=end, actions=False)
    other_technicals_tmp = yf.Ticker(ticker).info
    