from __future__ import print_function
import random
import yfinance as yf
import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from IPython.display import clear_output
from tqdm import tqdm
import pandas_datareader.data as web
import datetime
import argparse
import multiprocessing as mp
from multiprocessing.pool import ThreadPool
import Stock

input_data_path = 'ticker.txt'
ticker_cik = pd.read_csv(input_data_path, delimiter=',')
sym_cik = ticker_cik.copy(deep=True)
sym_cik.set_index('Ticker', inplace=True)
cik_sym = ticker_cik.copy(deep=True)
cik_sym.set_index('CIK', inplace=True)


#Settings of the algorithm
MARKET_CAP_TR = 5
DAY_CLOSE_TR = 30
VOLUME_TR = 2e6



# Looks up Edgar CIK Number
def symbol_to_cik(symbols):
    new_symbols = [i.lower() for i in symbols]
    cik = [sym_cik.loc[i, 'CIK'] for i in new_symbols]
    return cik


# Looks up Symbol from CIK Number:
def cik_to_symbol(ciks):
    tickers = [cik_sym.loc[i, 'Ticker'] for i in ciks]
    new_tickers = [i.upper() for i in tickers]
    return new_tickers


# Turns URL into Soup object
def to_soup(url):
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req).read()
    soup = BeautifulSoup(webpage, 'html.parser')
    return soup


def security_size(market_cap):
    thresholds = [0, 20e6, 50e6, 100e6, 150e6, 200e6, 500e6, 1e9, 2e9, 5e9, 10e9, 20e9, 1e14]
    labels = ['20M-', '50M', '100M', '150M', '200M', '500M', '1B', '2B', '5B', '10B', '20B', '20B+']
    for i in range(len(thresholds) - 1):
        if (market_cap >= thresholds[i]) & (market_cap < thresholds[i + 1]):
            security_category = labels[i]

    return security_category


def partition_to_sublists(list_in, partition_size):
    # looping till length list_in
    for i in range(0, len(list_in), partition_size):
        yield list_in[i:i + partition_size]


def contents_compiler(contents_):
    for row in range(len(contents_)):
        contents_[row][0] = int(contents_[row][0])
        if contents_[row][6][-1] == 'M':
            scalar = 1  # in million
        else:
            scalar = 1000  # in million
        contents_[row][6] = int(round(float(contents_[row][6][:-1])) * scalar)  # in million

        contents_[row][8] = float(contents_[row][8])
        contents_[row][9] = float(contents_[row][9][:-1])
        contents_[row][10] = int(contents_[row][10].replace(',', ''))




def scan_market(symbols, start_date, end_date=datetime.date.today(),
                volume_threshold=1.5, price_change_threshold=0.1, export_file=1):
    print('SCAN START for period beginning: ' + start_date)
    # if rand_set is True the algorithm checks rand_size random samples
    end_yahoo = end_date
    start_yahoo = start_date
    
    dataset = pd.DataFrame()
        
    for i in range(len(symbols)):
        if np.mod(i+1, 500):
            print(symbols[i]+' : '+str(i+1) + '  out of  ' + str(len(symbols)))
        try:
            try:
                day_technicals, other_technicals = Stock.get_data(symbols[i], start_yahoo, end_yahoo)
            except:
                print('Error fetching data from yahoo')
                continue
        
            if (other_technicals['marketCap'] > 5) or (day_technicals.iloc[-1]['Close'] > 30):
                continue    # large cap or expensive stocks, we pass this symbol (marketCap is normalized to 100M, so 5 means 500M)

            else:     # small cap and cheap stock, our interests
                for day_idx in range(3, len(day_technicals)-5):
                    # considering a window of 3 past days for every potential day,
                    # and predicting the price for the next 4 days
                    # (-5 is just a convention to ensure having enough days left for prediction)

                    conditions = []

                    # large enough volume today
                    conditions.append(day_technicals.iloc[day_idx]['Volume'] > 2e6)

                    # significantly higher volume than average
                    conditions.append(day_technicals.iloc[day_idx]['Volume'] >
                                      volume_threshold*other_technicals['averageVolume'])

                    # a change in the price
                    conditions.append(abs(day_technicals.iloc[day_idx]['Volume'] - day_technicals.iloc[day_idx-1]['Volume']) >
                                      price_change_threshold*day_technicals.iloc[day_idx-1]['Volume'])                    
                    if sum(conditions) == len(conditions):  # all True
                        print('--- Good ---')                    
                        target_price = np.array([day_technicals.iloc[day_idx + 1]['High'],
                                                 day_technicals.iloc[day_idx + 2]['High'],
                                                 day_technicals.iloc[day_idx + 3]['High'],
                                                 day_technicals.iloc[day_idx + 4]['High'],
                                                 max(day_technicals.iloc[day_idx+1:day_idx+5]['High'])
                                                 ])
                        target_price = (target_price/day_technicals.iloc[day_idx]['Close'] - 1)*100
                        new_sample = Stock.StockSample(symbols[i], today=day_technicals.iloc[day_idx].name, quote=other_technicals)                        
                        new_sample.Compute_features(Train=True, targets=list(target_price))                        
                        dataset = dataset.append(new_sample.df, ignore_index=True)
                        
        except:
            print(symbols[i],' : A problem Occured.')
            continue
    if dataset.empty:
        print('No good stock is found!')
    elif (export_file == 1):
        dataset.to_json('Data/dataset' + start_date + f'{random.randrange(1, 10**6):03}' + '.json', indent=4)

    print('SCAN COMPLETE for one chunk of tickers for period beginning: ' + start_date)

    return dataset


def scan_eod(symbols, day=datetime.date.today(),
                volume_threshold=1.5, price_change_threshold=0.1, export_file=1):
    #print('SCAN START for period beginning: ' + start_date)
    # we want to check the data of a specific day
    start_date = day    
    start_yahoo = day
    end_yahoo = day

    dataset = pd.DataFrame()

    for i in range(len(symbols)):        
        if np.mod(i+1, 500):
            print(str(i+1) + '  out of  ' + str(len(symbols)))
        try:
            today_technicals, other_technicals = Stock.get_data(symbols[i], start_yahoo, end_yahoo)
            if (other_technicals['marketCap'] > 800) or (today_technicals.iloc[-1]['Close'] > 30):
                print(symbols[i],': passing because large cap or expensive')
                # large cap or expensive stocks, we pass this symbol (marketCap is normalized to 100M, so 5 means 500M)
                continue    

            else:     
                # small cap and cheap stock, our interests
                for day_idx in range(1):
                    # considering last day 
                    # and predicting the price for the next 4 days

                    conditions = []

                    # large enough volume today
                    conditions.append(today_technicals.iloc[day_idx]['Volume'] > 2e6)

                    # significantly higher volume than average
                    conditions.append(today_technicals.iloc[day_idx]['Volume'] >
                                      volume_threshold*other_technicals['averageVolume'])

                    # a change in the price
                    conditions.append(abs(today_technicals.iloc[day_idx]['Volume'] - today_technicals.iloc[day_idx-1]['Volume']) >
                                      price_change_threshold*today_technicals.iloc[day_idx-1]['Volume'])

                    #if(True):
                    if sum(conditions) == len(conditions):  # all True
                        # Converting time to a proper format                        
                        today = datetime.datetime(int(day[:4]), int(day[5:7]), int(day[8:]))
                        new_sample = Stock.StockSample(symbols[i], today=today, quote=other_technicals)                        
                        new_sample.Compute_features()                        

                        dataset = dataset.append(new_sample.df, ignore_index=True)
        except:            
            print('A problem Occured.')
            continue
    if dataset.empty:
        print('No good stock is found!')
    elif (export_file == 1):
        dataset.to_json('Data/Test/EoD-dataset' + start_date + f'{random.randrange(1, 10**6):03}' + '.json', indent=4)

    print('SCAN COMPLETE for one chunk of tickers for period beginning: ' + start_date)

    return dataset


def to_do(items):
    # add short interest, higher short interests means higher breakout chance
    return items


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Market screener dataset')
    parser.add_argument('--tickers', default='complete', type=str,
                        help='Enter symbols you would like analyzed(Ex: "complete" for all tickers, "file" for searching in file, "random" for selecting randomly, or AAPL TSLA)')
    parser.add_argument('--ticker_file', default='ticker.txt', type=str,
                        help='Enter the file name where ticker list is stored')        
    parser.add_argument('--size', default=1000, type=int,
                        help='Number of stocks we want to monitor.')            
    parser.add_argument('--export', default=1, type=int, help='Export (0/1)')
    parser.add_argument('--parallel', default=0, type=int, help='Export (0/1)')
    parser.add_argument('--start_date', default='2020-12-05', type=str,
                        help='How far back would you like to go?(YYYY-MM-DD)')
    parser.add_argument('--end_date', default='2021-01-19', type=str,
                        help='End of the scan?(YYYY-MM-DD)')
    parser.add_argument('--eod', default=0, type=int, help='EoD scan (0/1)')

    args = parser.parse_args()

    
    all_tickers = args.tickers
    if all_tickers == 'complete':
        symbols_all = [str(i).upper() for i in ticker_cik.Ticker]
    elif all_tickers == 'random':
        idx = np.random.choice(range(len(ticker_cik)), size=args.size, replace=False)
        symbols_all = [str(i).upper() for i in ticker_cik.iloc[idx].Ticker]
    elif all_tickers == 'file':
        ticker_path = args.ticker_file
        selected_tickers = pd.read_csv(ticker_path)        
        symbols_all = [str(i).upper() for i in selected_tickers.Ticker]
    else:
        symbols_all = [i for i in all_tickers.split()]

    start_date = args.start_date
    end_date = args.end_date
    export_file = args.export

    if args.parallel == 0:
        if args.eod == 0:
            scan_market(symbols_all, start_date, end_date, export_file)
        else:
            scan_eod(symbols_all, end_date, export_file)
    else:
        core_num = mp.cpu_count()
        # nproc = core_num
        nproc = 10
        qout = mp.Queue()

        pool = mp.Pool(processes=nproc)

        symbols_list = partition_to_sublists(symbols_all, round(len(symbols_all) / nproc))
        if args.eod == 0:
            processes = pool.starmap(scan_market,
                                     [(symbols, start_date, end_date, export_file) for symbols in symbols_list])
        else:
            processes = pool.starmap(scan_eod,
                                     [(symbols, start_date, end_date, export_file) for symbols in symbols_list])

        pool.close()
        pool.join()

    # example1: python main_marketscan.py --tickers complete --start_date 2020-12-05 --end_date 2021-01-19 --export 1 --parallel 1 --eod 1
    # example2: python main_marketscan.py --tickers complete --start_date 2020-08-01 --export 1 --parallel 0
    # example3: python main_marketscan.py --tickers file --ticker_file ticker_h.txt --end_date 2021-01-27 --export 1 --parallel 0 --eod 1
    # example4: python main_marketscan.py --tickers random --size 20 --start_date 2020-01-01 --end_date 2021-01-27 --export 1 --parallel 0 --eod 0