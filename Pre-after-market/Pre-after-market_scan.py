import matplotlib.pyplot as plt
import requests
from bs4 import BeautifulSoup
import pandas as pd
import six
import numpy as np

def render_mpl_table(data, col_width=3.0, row_height=0.625, font_size=14,
                     header_color='#40466e', row_colors=['#f1f1f2', 'w'], edge_color='w',
                     bbox=[0, 0, 1, 1], header_columns=0,
                     ax=None, **kwargs):
    if ax is None:
        size = (np.array(data.shape[::-1]) + np.array([0, 1])) * np.array([col_width, row_height])
        fig, ax = plt.subplots(figsize=size)
        ax.axis('off')

    mpl_table = ax.table(cellText=data.values, bbox=bbox, colLabels=data.columns, **kwargs)

    mpl_table.auto_set_font_size(False)
    mpl_table.set_fontsize(font_size)

    for k, cell in  six.iteritems(mpl_table._cells):
        cell.set_edgecolor(edge_color)
        if k[0] == 0 or k[1] < header_columns:
            cell.set_text_props(weight='bold', color='w')
            cell.set_facecolor(header_color)
        else:
            cell.set_facecolor(row_colors[k[0]%len(row_colors) ])
    return ax



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

ax = plt.subplot(111, frame_on=False) # no visible frame
ax.xaxis.set_visible(False)  # hide the x axis
ax.yaxis.set_visible(False)  # hide the y axis

if soup.select("span.change--percent--q>bg-quote")[0].get('session') == 'pre':

    ax=render_mpl_table(premarket, header_columns=0, col_width=2.0)
    plt.savefig('PreMarket.png')    
    display(premarket)
elif soup.select("span.change--percent--q>bg-quote")[0].get('session') == 'after':
    ax=render_mpl_table(aftermarket, header_columns=0, col_width=2.0)
    plt.savefig('AfterMarket.png')    
    display(aftermarket)