from lib import ApiData

from datetime import datetime
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt

class Ichimoku(object):

    apiData = {}

    def __init__(self, api_account_id, api_access_token):
        self.apiData = ApiData.ApiData(api_account_id, api_access_token);

    def Verify(self, instrument, actual_price):
        dataS5 = self.apiData.GetData(instrument, "M1", 500);

        ichimoku_dataframe = pd.DataFrame()

        tenkan = self.CalculateMidPoint(dataS5['high'], dataS5['low'], 7);
        kijun = self.CalculateMidPoint(dataS5['high'], dataS5['low'], 22);
        senkou_span_a = ((tenkan + kijun) / 2).shift(22);
        senkou_span_b = self.CalculateMidPoint(dataS5['high'], dataS5['low'], 44).shift(22);
        chikou_span = dataS5['close'].shift(-22);

        ichimoku_dataframe['TENKAN'] = tenkan;
        ichimoku_dataframe['KIJUN'] = kijun;
        ichimoku_dataframe['SENKOU_A'] = senkou_span_a;
        ichimoku_dataframe['SENKOU_B'] = senkou_span_b;
        ichimoku_dataframe['CHIKOU'] = chikou_span;

        ichimoku_dataframe.fillna(method='ffill')
        ichimoku_dataframe.plot()
        plt.show()

    def CalculateMidPoint(self, high_prices, low_prices, window):
        maxHigh = pd.rolling_max(high_prices, window = window);
        maxLow = pd.rolling_min(low_prices, window = window);
        midPoint = (maxHigh + maxLow) / 2;

        return midPoint;
