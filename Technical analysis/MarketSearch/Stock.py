import pandas as pd
import yfinance as yf
import datetime as dt
import numpy as np

class StockSample(object):
    Date, Open, High, Close, VolumeNormalized, DayChange, OverNighCahange  = [], [], [], [], [], [], []
    ChartPatterns, IntraDayVolumeIndicator, OverDayVolumeIndicator, EoDtoHoD = [], [], [], []
    df = pd.DataFrame()
    duration = 4
    
    def __init__(self, ticker, today, quote, duration=4):
        self.symbol = ticker
        
        self.duration = duration
        # to get more data so as avoiding holidays and weekends
        start_date = str((today - dt.timedelta(duration+8)).date())  
        self.technicals_90m = self.get_90m_technical(start_date=start_date, end_date=today)
        self.day_technicals = self.get_daily_technical(start_date=start_date, end_date=today)
        self.other_technicals = quote
        

    def get_90m_technical(self, start_date, end_date):
        try:
            return yf.Ticker(self.symbol).history(start=start_date, end=end_date, interval="90m", actions=False)\
                .reset_index(level='Datetime')
        except:
            print('Something went wrong')
            return pd.DataFarame()

    def get_daily_technical(self, start_date, end_date):
        try:            
            return yf.Ticker(self.symbol).history(start=start_date, end=end_date, actions=False)
        except:
            print('Something went wrong')
            return pd.DataFarame()
        
    def Compute_features(self, Train=False, targets = []):
        quote = self.other_technicals
        duration = self.duration
       
        for i in range(duration):
            period_90m = [len(self.technicals_90m)-5*i-5, len(self.technicals_90m)-5*i]
            day_technicals_90m = self.technicals_90m.iloc[period_90m[0]:period_90m[1]]
            period_daily = [len(self.day_technicals)-i - 1, len(self.day_technicals)-i]
            day_technicals_daily = self.day_technicals.iloc[period_daily[0]:period_daily[1]]
            day_technicals_daily_yesterday = self.day_technicals.iloc[period_daily[0]-1:period_daily[1]-1]
            price_avg = (day_technicals_90m['Open']+day_technicals_90m['Close']+day_technicals_90m['High']+day_technicals_90m['Low'])/4
            chart_patterns_new, volume_indicator_new = get_category(price_avg.values, day_technicals_90m['Volume'].values,
                                                                    avg_volume=quote['averageVolume'])
    
            self.Date.append(str(day_technicals_daily.index.date[0]))
            self.Open.append(day_technicals_daily['Open'].values)
            self.High.append(day_technicals_daily['High'].values)
            self.Close.append(day_technicals_daily['Close'].values)
            self.VolumeNormalized.append(day_technicals_daily['Volume'].values/quote['averageVolume'])
            self.DayChange.append((day_technicals_daily['Close'].values/day_technicals_daily['Open'].values - 1)*100)
            self.OverNighCahange.append(((day_technicals_daily['Open'].values/day_technicals_daily_yesterday['Close'].values - 1)*100)[0])
            self.EoDtoHoD.append((day_technicals_daily['Close'].values / day_technicals_daily['High'].values - 1) * 100)
            self.ChartPatterns.append(chart_patterns_new)
            self.IntraDayVolumeIndicator.append(volume_indicator_new)

        new_sample_data = {'ticker': self.symbol, 'sector': quote['sector'], 'industry': quote['industry'],
                           'heldPercentInsiders': quote['heldPercentInsiders'],
                           'heldPercentInstitutions': quote['heldPercentInstitutions'],
                           'regularMarketVolume': quote['regularMarketVolume'],
                           'fiftyTwoWeekHigh': quote['fiftyTwoWeekHigh'],
                           'fiftyTwoWeekLow': quote['fiftyTwoWeekLow'],
                           'averageDailyVolume10Day': quote['averageDailyVolume10Day'],
                           'fiftyDayAverage': quote['fiftyDayAverage'],
                           'averageVolume': quote['averageVolume'],
                           'marketCap': quote['marketCap'],
                           'Date-0': self.Date[0], 'Open-0': self.Open[0], 'High-0': self.High[0], 'Close-0': self.Close[0],
                           'VolumeNormalized-0': self.VolumeNormalized[0], 'DayChange-0': self.DayChange[0],
                           'OverNighCahange-0': self.OverNighCahange[0],
                           'EoDtoHoD-0': self.EoDtoHoD[0], 'OverDayVolumeIndicator-0': self.VolumeNormalized[0]/self.VolumeNormalized[1],
                           'ChartPatterns-0': self.ChartPatterns[0], 'IntraDayVolumeIndicator-0': self.IntraDayVolumeIndicator[0],
                           'Date-1': self.Date[1], 'Open-1': self.Open[1], 'High-1': self.High[1], 'Close-1': self.Close[1],
                           'VolumeNormalized-1': self.VolumeNormalized[1], 'DayChange-1': self.DayChange[1],
                           'OverNighCahange-1': self.OverNighCahange[1],
                           'EoDtoHoD-1': self.EoDtoHoD[1],  'OverDayVolumeIndicator-1': self.VolumeNormalized[1]/self.VolumeNormalized[2],
                           'ChartPatterns-1': self.ChartPatterns[1], 'IntraDayVolumeIndicator-1': self.IntraDayVolumeIndicator[1],
                           'Date-2': self.Date[2], 'Open-2': self.Open[2], 'High-2': self.High[2], 'Close-2': self.Close[2],
                           'VolumeNormalized-2': self.VolumeNormalized[2], 'DayChange-2': self.DayChange[2],
                           'OverNighCahange-2': self.OverNighCahange[2],
                           'EoDtoHoD-2': self.EoDtoHoD[2],  'OverDayVolumeIndicator-2': self.VolumeNormalized[2]/self.VolumeNormalized[3],
                           'ChartPatterns-2': self.ChartPatterns[2], 'IntraDayVolumeIndicator-2': self.IntraDayVolumeIndicator[2],
                           'Date-3': self.Date[3], 'Open-3': self.Open[3], 'High-3': self.High[3], 'Close-3': self.Close[3],
                           'VolumeNormalized-3': self.VolumeNormalized[3], 'DayChange-3': self.DayChange[3],
                           'OverNighCahange-3': self.OverNighCahange[3],
                           'EoDtoHoD-3': self.EoDtoHoD[3],
                           'ChartPatterns-3': self.ChartPatterns[3], 'IntraDayVolumeIndicator-3': self.IntraDayVolumeIndicator[3]
                           }
        if Train==True:
            # Add target values to the data frame
            target_d = {'Label1-MaxGainInDay1': targets[0], 
                        'Label2-MaxGainInDay2': targets[1],
                        'Label3-MaxGainInDay3': targets[2], 
                        'Label4-MaxGainInDay4': targets[3],
                        'Label5-MaxGainIn4Days': targets[4]}
            new_sample_data.update(target_d)
        self.df = pd.DataFrame(new_sample_data)
        


def get_data(symbol, start, end):
    """
    Get technicals for tickers.
    Documentation: https://aroussi.com/post/python-yahoo-finance
    :param period: data period to download, 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max. Either Use period parameter or use start and end.
    :param interval: data interval, 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo. Intraday data cannot extend last 60 days.
    :param start: Start day (if not using period) in string, YYYY-MM-DD or datetime.
    :param end: End day (if not using period) in string (YYYY-MM-DD) or datetime.
    :param prepost: Include Pre and Post market data in results? (Default is False)
    :param actions: Download stock dividends and stock splits events? (Default is True)

    :return:

    example: yf.Ticker("AAPL").history(start=start, end=end, prepost=True, interval='1h', actions=False)
    """

    # data = yf.Ticker(symbol).history(start=start, end=end, actions=False)
    day_technicals = yf.Ticker(symbol).history(start=start, end=end, actions=False)


    other_technicals_tmp = yf.Ticker(symbol).info

    other_technicals = pd.Series({'quoteType': other_technicals_tmp['quoteType'],
                                  'sector': other_technicals_tmp['sector'],
                                  'industry': other_technicals_tmp['industry'],
                                  'sharesOutstanding': other_technicals_tmp['sharesOutstanding'],
                                  'heldPercentInsiders': other_technicals_tmp['heldPercentInsiders'],
                                  'heldPercentInstitutions': other_technicals_tmp['heldPercentInstitutions'],
                                  'regularMarketVolume': other_technicals_tmp['regularMarketVolume'],
                                  'fiftyTwoWeekHigh': other_technicals_tmp['fiftyTwoWeekHigh'],
                                  'fiftyTwoWeekLow': other_technicals_tmp['fiftyTwoWeekLow'],
                                  'averageDailyVolume10Day': other_technicals_tmp['averageDailyVolume10Day'],
                                  'fiftyDayAverage': other_technicals_tmp['fiftyDayAverage'],
                                  'averageVolume': other_technicals_tmp['averageVolume'],
                                  'marketCap': other_technicals_tmp['marketCap']/100e6,
                                  })



    return day_technicals, other_technicals


    
def get_category(price_data, volume_data, avg_volume):
    # chart patter: categorical output.
    # 1: flat: not so much changes during he day, mostly consolidating
    # 2: downfall shape, strong start-of-day and weak end-of-day
    # 3: bell shape closer  to the market open with some high strength during regular hours but not close to the bells
    # 4: bell shape closer  to the market close with some high strength during regular hours but not close to the bells
    # 5: uprise: almost constant growth during the day and strong close near high of the day
    # 6: recovery: going down and trying to recover toward the end
    # 7: mexican hat: going down and trying to recover but again going down toward the end-of-day

    normalized_moves = np.diff(price_data)/price_data[0:-1]

    threshold_price = 0.07          # threshold to detect changes = 7%
    # move_directions: 0, -1, +1, showing not changing, increased ore than 10%, and decreased more than 10%
    move_directions = np.array(np.sign(normalized_moves) * (abs(normalized_moves) > threshold_price), dtype='int32')

    if (move_directions == [-1, -1, -1, -1]).all():
        chart_patterns = 2
    elif (move_directions == [-1, -1, -1, 0]).all():
        chart_patterns = 2
    elif (move_directions == [-1, -1, -1, 1]).all():
        chart_patterns = 6
    elif (move_directions == [-1, -1, 0, -1]).all():
        chart_patterns = 2
    elif (move_directions == [-1, -1, 0, 0]).all():
        chart_patterns = 2
    elif (move_directions == [-1, -1, 0, 1]).all():
        chart_patterns = 6
    elif (move_directions == [-1, -1, 1, -1]).all():
        chart_patterns = 7
    elif (move_directions == [-1, -1, 1, 0]).all():
        chart_patterns = 6
    elif (move_directions == [-1, -1, 1, 1]).all():
        chart_patterns = 6
    elif (move_directions == [-1, 0, -1, -1]).all():
        chart_patterns = 2
    elif (move_directions == [-1, 0, -1, 0]).all():
        chart_patterns = 2
    elif (move_directions == [-1, 0, -1, 1]).all():
        chart_patterns = 6
    elif (move_directions == [-1, 0, 0, -1]).all():
        chart_patterns = 2
    elif (move_directions == [-1, 0, 0, 0]).all():
        chart_patterns = 2
    elif (move_directions == [-1, 0, 0, 1]).all():
        chart_patterns = 6
    elif (move_directions == [-1, 0, 1, -1]).all():
        chart_patterns = 7
    elif (move_directions == [-1, 0, 1, 0]).all():
        chart_patterns = 6
    elif (move_directions == [-1, 0, 1, 1]).all():
        chart_patterns = 6
    elif (move_directions == [-1, 1, -1, -1]).all():
        chart_patterns = 7
    elif (move_directions == [-1, 1, -1, 0]).all():
        chart_patterns = 7
    elif (move_directions == [-1, 1, -1, 1]).all():
        chart_patterns = 6
    elif (move_directions == [-1, 1, 0, -1]).all():
        chart_patterns = 7
    elif (move_directions == [-1, 1, 0, 0]).all():
        chart_patterns = 6
    elif (move_directions == [-1, 1, 0, 1]).all():
        chart_patterns = 6
    elif (move_directions == [-1, 1, 1, -1]).all():
        chart_patterns = 7
    elif (move_directions == [-1, 1, 1, 0]).all():
        chart_patterns = 6
    elif (move_directions == [-1, 1, 1, 1]).all():
        chart_patterns = 6
    elif (move_directions == [0, -1, -1, -1]).all():
        chart_patterns = 2
    elif (move_directions == [0, -1, -1, 0]).all():
        chart_patterns = 2
    elif (move_directions == [0, -1, -1, 1]).all():
        chart_patterns = 6
    elif (move_directions == [0, -1, 0, -1]).all():
        chart_patterns = 2
    elif (move_directions == [0, -1, 0, 0]).all():
        chart_patterns = 2
    elif (move_directions == [0, -1, 0, 1]).all():
        chart_patterns = 6
    elif (move_directions == [0, -1, 1, -1]).all():
        chart_patterns = 7
    elif (move_directions == [0, -1, 1, 0]).all():
        chart_patterns = 6
    elif (move_directions == [0, -1, 1, 1]).all():
        chart_patterns = 6
    elif (move_directions == [0, 0, -1, -1]).all():
        chart_patterns = 2
    elif (move_directions == [0, 0, -1, 0]).all():
        chart_patterns = 2
    elif (move_directions == [0, 0, -1, 1]).all():
        chart_patterns = 6
    elif (move_directions == [0, 0, 0, -1]).all():
        chart_patterns = 2
    elif (move_directions == [0, 0, 0, 0]).all():
        chart_patterns = 1
    elif (move_directions == [0, 0, 0, 1]).all():
        chart_patterns = 5
    elif (move_directions == [0, 0, 1, -1]).all():
        chart_patterns = 4
    elif (move_directions == [0, 0, 1, 0]).all():
        chart_patterns = 5
    elif (move_directions == [0, 0, 1, 1]).all():
        chart_patterns = 5
    elif (move_directions == [0, 1, -1, -1]).all():
        chart_patterns = 3
    elif (move_directions == [0, 1, -1, 0]).all():
        chart_patterns = 3
    elif (move_directions == [0, 1, -1, 1]).all():
        chart_patterns = 5
    elif (move_directions == [0, 1, 0, -1]).all():
        chart_patterns = 4
    elif (move_directions == [0, 1, 0, 0]).all():
        chart_patterns = 5
    elif (move_directions == [0, 1, 0, 1]).all():
        chart_patterns = 5
    elif (move_directions == [0, 1, 1, -1]).all():
        chart_patterns = 4
    elif (move_directions == [0, 1, 1, 0]).all():
        chart_patterns = 5
    elif (move_directions == [0, 1, 1, 1]).all():
        chart_patterns = 5
    elif (move_directions == [1, -1, -1, -1]).all():
        chart_patterns = 2
    elif (move_directions == [1, -1, -1, 0]).all():
        chart_patterns = 2
    elif (move_directions == [1, -1, -1, 1]).all():
        chart_patterns = 6
    elif (move_directions == [1, -1, 0, -1]).all():
        chart_patterns = 2
    elif (move_directions == [1, -1, 0, 0]).all():
        chart_patterns = 2
    elif (move_directions == [1, -1, 0, 1]).all():
        chart_patterns = 6
    elif (move_directions == [1, -1, 1, -1]).all():
        chart_patterns = 7
    elif (move_directions == [1, -1, 1, 0]).all():
        chart_patterns = 6
    elif (move_directions == [1, -1, 1, 1]).all():
        chart_patterns = 6
    elif (move_directions == [1, 0, -1, -1]).all():
        chart_patterns = 2
    elif (move_directions == [1, 0, -1, 0]).all():
        chart_patterns = 2
    elif (move_directions == [1, 0, -1, 1]).all():
        chart_patterns = 6
    elif (move_directions == [1, 0, 0, -1]).all():
        chart_patterns = 2
    elif (move_directions == [1, 0, 0, 0]).all():
        chart_patterns = 5
    elif (move_directions == [1, 0, 0, 1]).all():
        chart_patterns = 5
    elif (move_directions == [1, 0, 1, -1]).all():
        chart_patterns = 4
    elif (move_directions == [1, 0, 1, 0]).all():
        chart_patterns = 5
    elif (move_directions == [1, 0, 1, 1]).all():
        chart_patterns = 5
    elif (move_directions == [1, 1, -1, -1]).all():
        chart_patterns = 3
    elif (move_directions == [1, 1, -1, 0]).all():
        chart_patterns = 3
    elif (move_directions == [1, 1, -1, 1]).all():
        chart_patterns = 5
    elif (move_directions == [1, 1, 0, -1]).all():
        chart_patterns = 4
    elif (move_directions == [1, 1, 0, 0]).all():
        chart_patterns = 5
    elif (move_directions == [1, 1, 0, 1]).all():
        chart_patterns = 5
    elif (move_directions == [1, 1, 1, -1]).all():
        chart_patterns = 4
    elif (move_directions == [1, 1, 1, 0]).all():
        chart_patterns = 5
    elif (move_directions == [1, 1, 1, 1]).all():
        chart_patterns = 5
    else:
        chart_patterns = 1


    # Both of these thresholds should be changed, as Yahoo does not give average volume at some days in the past.
    # So perhaps after some breakout and higher volumes, we observe a different 10DaysAvgVolume and AverageVolume,
    # compared to what should have been there actually to build a proper dataset.
    volume_threshold1 = 0.1
    volume_threshold2 = 0.05
    if (volume_data[4] >= max(volume_data) * volume_threshold1) and (volume_data[4]*5 > volume_threshold2 * avg_volume):
        volume_indicator = 1    # cold keep its high volume and strength
    else:
        volume_indicator = 0

    return chart_patterns, volume_indicator


def unusual_screener(export_file=0):
    print('SCAN START for period beginning: ' + start_date)

    url = 'https://finviz.com/screener.ashx?v=111&s=ta_unusualvolume&f=cap_microunder,geo_usa,sh_curvol_o10000,sh_relvol_o5,sh_short_u10&o=-change'
    page_soup = to_soup(url)
    contentTable = page_soup.find('div', {'id': 'screener-content'})
    contents_ = []
    rows = contentTable.findAll(lambda tag: tag.name == "tr" and tag.has_attr('class') == True)
    headers = ['no', 'Ticker', 'Company', 'Sector', 'Industry', 'Country', 'MarketCap', 'P/E', 'Price', 'Change', 'Volume']
    for row in rows:
        contents_list = row.find_all('td')
        row_content = [contents_list[i].text for i in range(len(contents_list))]
        contents_.append(row_content)

    contents_compiler(contents_)
    contents = pd.DataFrame(contents_, columns=headers).drop(columns=['no', 'country', 'P/E'])

    return contents
