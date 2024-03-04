from yahoofinancials import YahooFinancials
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd

ticker = 'ZM'
yf = YahooFinancials(ticker)
start = dt.datetime.today() - dt.timedelta(120)

end = dt.datetime.today()

data = yf.get_historical_price_data(start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'), 'daily')

data_pd = pd.DataFrame(data[ticker]['prices'])[['formatted_date','adjclose']]
data_pd.set_index('formatted_date',inplace=True)
data_pd.dropna(inplace=True)


plt.plot(data_pd['adjclose'])
plt.xticks(data_pd.index[0:-1:30])
