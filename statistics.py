import datetime as dt
import yfinance as yf
import pandas as pd



stocks=['AMZN','MSFT']

start = dt.datetime.today() - dt.timedelta(300)

end = dt.datetime.today()

cl_Price = pd.DataFrame()
daily_return = pd.DataFrame()

for ticker in stocks:
    cl_Price[ticker] = yf.download(ticker, start, end)['Adj Close']
    daily_return[ticker] = cl_Price[ticker].pct_change()

print(daily_return.mean())
print(daily_return.std())
print(daily_return.median())

#A Moving Average
daily_return_avg = daily_return.rolling(window=10).mean()
print(daily_return_avg)

#Exponential Weighted Moving Average
# Put more weights on the last values than older ones
daily_return_ExpAvg = daily_return.ewm(span=10,min_periods=10).mean()
print(daily_return_ExpAvg)
    
    
    