import datetime as dt
import yfinance as yf
import pandas as pd


start = '2020-03-01'
end = '2021-01-25'

cl_Price = pd.DataFrame()

input_data_path = 'ticker.txt'
ticker_cik = pd.read_csv(input_data_path, delimiter=',')
symbols_all = [str(i).upper() for i in ticker_cik.Ticker]

symbols_selected = pd.DataFrame(columns=["Ticker"])


counter = 0
for ticker in symbols_all:
    
    counter += 1
    try:
        other_technicals_tmp = yf.Ticker(ticker).info
        symbols_selected = symbols_selected.append({"Ticker":ticker},ignore_index=True)
        print(ticker)
    except:
        print(ticker,' : problem' )
    
    if counter%100 ==0:
        symbols_selected.to_csv('Ticker_selected.csv', index=False)
        
    