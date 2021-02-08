from __future__ import print_function
import random
import yfinance as yf
from os import walk
import requests
import pandas as pd
import numpy as np
import datetime
import argparse
import multiprocessing as mp



def load_data(input_data_path, filenames):
    # merge datasets available on the output folder
    dfs = []
    for file in filenames:
        dfs.append(pd.read_json(input_data_path + file))

    return pd.concat(dfs)


def inputs_def():
    """
    # Date-x: str: dates of the sample (Date-0 is today and we aim to predict price action in the next 4 days)
    # averageDailyVolume10Day: Average volume of the last 10 days. Notice that due to limitation of Yahoo, we could not
                               put the true average at Date-0. Rather, we just put the current daily avg volume.
                               Should be fine in reality since Yahoo gives these info for actual today
                               (which we need in the operation mode).
    # averageVolume: float: Average volume of the ticker. Notice that due to limitation of Yahoo, we could not
                            put the true average at Date-0. Rather, we just put the current daily avg volume.
                            Should be fine in reality since Yahoo gives these info for actual today
                            (which we need in the operation mode).
    # VolumeNormalized-x: Volume of Date-x divided by the averageVolume
    # IntraDayVolumeIndicator-x: binary (1: could keep its high volume and strength during Date-x)

    # ChartPatterns-x: categorical: chart pattern for Date-x.
                    1: flat: not so much changes during he day, mostly consolidating
                    2: downfall shape, strong start-of-day and weak end-of-day
                    3: bell shape closer  to the market open with some high strength during regular hours but not close to the bells
                    4: bell shape closer  to the market close with some high strength during regular hours but not close to the bells
                    5: uprise: almost constant growth during the day and strong close near high of the day
                    6: recovery: going down and trying to recover toward the end
                    7: mexican hat: going down and trying to recover but again going down toward the end-of-day
    # marketCap: float: market cap in 100M
    # Open-x: float: Price at the Open of the Date-x (Open-1 means opening price of the last trading day)
    # Close-x: float: Price at the End of the Date-x (Close-1 means EoD of last trading day)
    # High-x: float: Price at High of the Date-x (High-1 means high of last trading day)
    # EoDtoHoD-x: float: EoD/HoD for Date-x
    # OverNighCahange-x: float: relative change at the tomorrow's opening (captures after hours and premarket moves)
    # fiftyDayAverage: float: suffers from the same problem as averageVolume.
                             Yahoo gives most recent value not the one on Date-0
    # fiftyTwoWeekHigh: float: 52-weeks high of the price

    # marketCap: float: market cap in 100M
    # heldPercentInstitutions: float in [0,1]

    # Labels: max potential gain in Day 1 (tomorrow), Day 2, 3, and 4, and max over all these 4 days.

    """


input_data_path = './Data/'

_, _, filenames = next(walk(input_data_path))

data = load_data(input_data_path, filenames)
