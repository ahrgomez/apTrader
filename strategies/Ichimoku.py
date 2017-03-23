from lib import ApiData

from datetime import datetime
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt

class Ichimoku(object):

    apiData = {};
    actual_index = 0;
    ichimoku_dataframe = pd.DataFrame();

    def __init__(self, api_account_id, api_access_token):
        self.apiData = ApiData.ApiData(api_account_id, api_access_token);

    def Verify(self, instrument, actual_price):
        self._calculateIchimokuLines(instrument);


    def _calculateIchimokuLines(self, instrument):
        dataS5 = self.apiData.GetData(instrument, "M1", 500);

        self.ichimoku_dataframe['TENKAN'] = self._calculateMidPoint(dataS5['high'], dataS5['low'], 7);
        self.ichimoku_dataframe['KIJUN'] = self._calculateMidPoint(dataS5['high'], dataS5['low'], 22);
        self.ichimoku_dataframe['SENKOU_A'] = ((self.ichimoku_dataframe['TENKAN'] + self.ichimoku_dataframe['KIJUN']) / 2).shift(22);
        self.ichimoku_dataframe['SENKOU_B'] = self._calculateMidPoint(dataS5['high'], dataS5['low'], 44).shift(22);
        self.ichimoku_dataframe['CHIKOU'] = dataS5['close'].shift(-22);

        actual_index = len(self.ichimoku_dataframe['KIJUN'].dropnan().index)

        print actual_index;

    def _isPriceTopOfKumo(self, actual_price):

        if actual_price >1:
            print "hola"

    def _calculateMidPoint(self, high_prices, low_prices, window):
        maxHigh = pd.rolling_max(high_prices, window = window);
        maxLow = pd.rolling_min(low_prices, window = window);
        midPoint = (maxHigh + maxLow) / 2;

        return midPoint;
