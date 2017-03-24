from lib import ApiData

from datetime import datetime
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
from shapely.wkt import loads as load_wkt

class Ichimoku(object):

    apiData = {};
    ichimoku_dataframe = pd.DataFrame();

    def __init__(self, api_account_id, api_access_token):
        self.apiData = ApiData.ApiData(api_account_id, api_access_token);

    def Verify(self, instrument, actual_price):

        self._calculateIchimokuLines(instrument, actual_price);

        if self._isPriceBottomOfKumo(actual_price):
            print "YES"
        else:
            print "NO"

        stop_loss_price =  self._getStopLossPrice();
        cross_point, cross_value = self._getLastCross();

        print cross_point
        print "-----"
        print cross_value

    def _calculateIchimokuLines(self, instrument, actual_price):
        dataS5 = self.apiData.GetData(instrument, "M1", 500);

        dataS5 = dataS5.append({ 'time': datetime.now(),
    			'high': actual_price,
    			'low': actual_price,
    			'close': actual_price}, ignore_index=True)

        self.ichimoku_dataframe['TENKAN'] = self._calculateMidPoint(dataS5['high'], dataS5['low'], 7);
        self.ichimoku_dataframe['KIJUN'] = self._calculateMidPoint(dataS5['high'], dataS5['low'], 22);
        self.ichimoku_dataframe['SENKOU_A'] = ((self.ichimoku_dataframe['TENKAN'] + self.ichimoku_dataframe['KIJUN']) / 2).shift(22);
        self.ichimoku_dataframe['SENKOU_B'] = self._calculateMidPoint(dataS5['high'], dataS5['low'], 44).shift(22);
        self.ichimoku_dataframe['CHIKOU'] = dataS5['close'].shift(-22);

        #self.ichimoku_dataframe.plot()
        #plt.show()

    def _isPriceTopOfKumo(self, actual_price):

        if actual_price > self.ichimoku_dataframe['SENKOU_A'].iloc[len(self.ichimoku_dataframe['SENKOU_A'].index) - 1]:
            if actual_price > self.ichimoku_dataframe['SENKOU_B'].iloc[len(self.ichimoku_dataframe['SENKOU_B'].index) - 1]:
                return True;

        return False;

    def _isPriceBottomOfKumo(self, actual_price):

        if actual_price < self.ichimoku_dataframe['SENKOU_A'].iloc[len(self.ichimoku_dataframe['SENKOU_A'].index) - 1]:
            if actual_price < self.ichimoku_dataframe['SENKOU_B'].iloc[len(self.ichimoku_dataframe['SENKOU_B'].index) - 1]:
                return True;

        return False;

    def _getStopLossPrice(self):
        return self.ichimoku_dataframe['TENKAN'].iloc[len(self.ichimoku_dataframe['TENKAN'].index) - 1]

    def _getLastCross(self):
        index = len(self.ichimoku_dataframe['TENKAN'].index) - 1;
        cross_point = None;
        cross_value = 0;
        actual_value = 0;

        tenkan_point = self.ichimoku_dataframe['TENKAN'].iloc[index];
        kijun_point = self.ichimoku_dataframe['KIJUN'].iloc[index];

        if tenkan_point > kijun_point:
            actual_value = 1;
        elif kijun_point > tenkan_point:
            actual_value = -1;
        else:
            actual_value = 0;

        while (cross_point is None):

            if (tenkan_point > kijun_point and actual_value != 1) or (kijun_point > tenkan_point and actual_value != -1) or (tenkan_point == kijun_point and actual_value != 0):
                    print "CRUCE!!!"
                    cross_value = self._getTypeOfCross(index, tenkan_point, kijun_point)

                    index = index + 1
                    new_tenkan = self.ichimoku_dataframe['TENKAN'].iloc[index]
                    new_kijun = self.ichimoku_dataframe['KIJUN'].iloc[index]

                    #if cross_value == 1:
                    #points = , ;
                    #else:
                    #    points = np.array([tenkan_point, new_kijun, new_tenkan, kijun_point]);

                    cross_point = self._calculateCrossPoint(np.sort(np.array([tenkan_point, kijun_point])), np.sort(np.array([new_tenkan, new_kijun])));
                    break;

            index = index - 1;
            tenkan_point = self.ichimoku_dataframe['TENKAN'].iloc[index];
            kijun_point = self.ichimoku_dataframe['KIJUN'].iloc[index];

        return cross_point, cross_value;

    def _calculateCrossPoint(self, points_left, points_right):
        points = np.array([points_left[1], points_right[1], points_right[0], points_left[0], points_left[1]]);

        df = pd.DataFrame(points);
        #df['TENKAN'] = [points[0], points[2]]
        #df['KINJUN'] = [points[1], points[3]]
        df.plot()
        plt.show()
        inpt = "POLYGON((1.0 " + str(points[0]) + ",2.0 " + str(points[1]) + ",3.0 " + str(points[2]) + ",4.0 " + str(points[3]) + ",1.0 " + str(points[0]) + "))";
        p1 = load_wkt(inpt);
        return p1.centroid.coords.xy[1][0];

    def _getTypeOfCross(self, index, tenkan_point, kijun_point):
        if tenkan_point > kijun_point:
            return -1;
        elif kijun_point > tenkan_point:
            return 1;
        else:
            index_aux = index - 1
            aux_tenkan = tenkan_point;
            aux_kijun = kijun_point;
            while(aux_tenkan == aux_kijun):
                index_aux = index_aux - 1
                aux_tenkan = self.ichimoku_dataframe['TENKAN'].iloc[index_aux]
                aux_kijun = self.ichimoku_dataframe['KIJUN'].iloc[index_aux]

                if aux_tenkan > aux_kijun:
                    return -1;
                elif aux_kijun > aux_tenkan:
                    return 1;
        return None;

    def _calculateMidPoint(self, high_prices, low_prices, window):
        maxHigh = high_prices.rolling(window=window,center=False).max();
        maxLow = low_prices.rolling(window=window,center=False).min();
        midPoint = (maxHigh + maxLow) / 2;

        return midPoint;
