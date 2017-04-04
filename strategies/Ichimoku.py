from lib.ApiData import ApiData

from datetime import datetime
from numpy import *
import numpy as np
import pandas as pd

class Ichimoku(object):

    apiData = {};
    ichimoku_dataframe = pd.DataFrame();
    granularity = "H1";

    def __init__(self):
        self.apiData = ApiData();

    def Verify(self, instrument, actual_price):

        self._calculateIchimokuLines(instrument, actual_price);

        if self._isEquilibriumZone(1):
            return None, -1;

        #LONG
        if self._isPriceTopOfKumo(actual_price):
            last_tenkan = self.ichimoku_dataframe['TENKAN'].iloc[len(self.ichimoku_dataframe['TENKAN'].index) - 1]
            if self._isPriceTopOfKumo(last_tenkan):
                cross_point, cross_value, candles_of_cross = self._getLastCross(self.ichimoku_dataframe['PRICE'], self.ichimoku_dataframe['TENKAN']);
                if cross_value == 1 and candles_of_cross < 6:
                    last_candle = self.apiData.GetLastClosedCandle(instrument, self.granularity);

                    if last_candle['open'] < last_tenkan and last_candle['close'] > last_tenkan:
                        if self._isCandleInAValidPosition(last_candle, cross_value):
                            stop_loss_price =  self._getStopLossPrice(cross_value);
                            return 1, stop_loss_price;
        elif self._isPriceBottomOfKumo(actual_price):
            last_tenkan = self.ichimoku_dataframe['TENKAN'].iloc[len(self.ichimoku_dataframe['TENKAN'].index) - 1]
            if self._isPriceBottomOfKumo(last_tenkan):
                cross_point, cross_value, candles_of_cross = self._getLastCross(self.ichimoku_dataframe['PRICE'], self.ichimoku_dataframe['TENKAN']);
                if cross_value == -1 and candles_of_cross < 6:
                    last_candle = self.apiData.GetLastClosedCandle(instrument, self.granularity);

                    if last_candle['open'] > last_tenkan and last_candle['close'] < last_tenkan:
                        if self._isCandleInAValidPosition(last_candle, cross_value):
                            stop_loss_price =  self._getStopLossPrice(cross_value);
                            return -1, stop_loss_price;

        return None, -1;

    def Verify2(self, instrument, actual_price):

        self._calculateIchimokuLines(instrument, actual_price);

        if self._isPriceInnerOfKumo(actual_price):
            return None, -1;

        cross_point, cross_value, minutes_of_cross = self._getLastCross(self.ichimoku_dataframe['TENKAN'], self.ichimoku_dataframe['KIJUN']);

        last_candles = self.apiData.GetData(instrument, self.granularity, 5)
        last_candle = last_candles.iloc[len(last_candles) - 2];

        if self._isCandleInAValidPosition(last_candle, cross_value) == False:
            return None, -1;

        #if minutes < 10:
        if self._isEquilibriumZone(minutes_of_cross):
            return None, -1;

        position_into_kumo = self._getPositionOfCross(cross_point, minutes_of_cross);
        stop_loss_price =  self._getStopLossPrice(cross_value);

        if cross_value == 1:
            #LONG
            #if position_into_kumo > -1:
            return 1, stop_loss_price;
        else:
            #SHORT
            #if position_into_kumo < 1:
            return -1, stop_loss_price;

        return None, -1;

    def _calculateIchimokuLines(self, instrument, actual_price):
        dataS5 = self.apiData.GetData(instrument, self.granularity, 500);

        dataS5 = dataS5.append({ 'time': datetime.now(),
    			'high': actual_price,
    			'low': actual_price,
    			'close': actual_price}, ignore_index=True)

        self.ichimoku_dataframe['TENKAN'] = self._calculateMidPoint(dataS5['high'], dataS5['low'], 7);
        self.ichimoku_dataframe['KIJUN'] = self._calculateMidPoint(dataS5['high'], dataS5['low'], 22);
        self.ichimoku_dataframe['SENKOU_A'] = ((self.ichimoku_dataframe['TENKAN'] + self.ichimoku_dataframe['KIJUN']) / 2).shift(22);
        self.ichimoku_dataframe['SENKOU_B'] = self._calculateMidPoint(dataS5['high'], dataS5['low'], 44).shift(22);
        self.ichimoku_dataframe['CHIKOU'] = dataS5['close'].shift(-22);
        self.ichimoku_dataframe['PRICE'] = dataS5['close'];

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

    def _isPriceInnerOfKumo(self, actual_price):
        if self._isPriceTopOfKumo(actual_price) == False and self._isPriceBottomOfKumo(actual_price) == False:
            return True;
        else:
            return False;

    def _getPositionOfCross(self, cross_point, minutes):

        if cross_point > self.ichimoku_dataframe['SENKOU_A'].iloc[len(self.ichimoku_dataframe['SENKOU_A'].index) - minutes]:
            if cross_point > self.ichimoku_dataframe['SENKOU_B'].iloc[len(self.ichimoku_dataframe['SENKOU_A'].index) - minutes]:
                return 1;
        if cross_point < self.ichimoku_dataframe['SENKOU_A'].iloc[len(self.ichimoku_dataframe['SENKOU_A'].index) - minutes]:
            if cross_point < self.ichimoku_dataframe['SENKOU_B'].iloc[len(self.ichimoku_dataframe['SENKOU_A'].index) - minutes]:
                return -1;

        return 0;

    def _getStopLossPrice(self, trade_type):
        senkouA = self.ichimoku_dataframe['SENKOU_A'].iloc[len(self.ichimoku_dataframe['SENKOU_A'].index) - 1];
        senkouB = self.ichimoku_dataframe['SENKOU_B'].iloc[len(self.ichimoku_dataframe['SENKOU_B'].index) - 1];
        if trade_type == 1:
            if senkouA < senkouB:
                return senkouA;
            else:
                return senkouB;
        else:
            if senkouA > senkouB:
                return senkouA;
            else:
                return senkouB;

    def _getLastCross(self, data1, data2):
        total_index = len(data1.index) - 1;
        index = total_index;
        cross_point = None;
        cross_value = 0;
        actual_value = 0;

        tenkan_point = data1.iloc[index];
        kijun_point = data2.iloc[index];

        if tenkan_point > kijun_point:
            actual_value = 1;
        elif kijun_point > tenkan_point:
            actual_value = -1;
        else:
            actual_value = 0;

        while (cross_point is None):

            if (tenkan_point > kijun_point and actual_value != 1) or (kijun_point > tenkan_point and actual_value != -1) or (tenkan_point == kijun_point and actual_value != 0):
                    cross_value = self._getTypeOfCross(index, tenkan_point, kijun_point)

                    index = index + 1
                    new_tenkan = data1.iloc[index]
                    new_kijun = data2.iloc[index]

                    tenkan_line = np.array([tenkan_point, new_tenkan]);
                    kijun_line = np.array([kijun_point, new_kijun]);
                    cross_point = self._calculateCrossPoint(tenkan_line, kijun_line);
                    break;

            index = index - 1;
            tenkan_point = data1.iloc[index];
            kijun_point = data2.iloc[index];

        return cross_point, cross_value, total_index - index + 1;

    def perp(self, a):
        b = empty_like(a)
        b[0] = -a[1]
        b[1] = a[0]
        return b

    def _calculateCrossPoint(self, line_1, line_2):
        a1 = np.array([1, line_1[0]])
        a2 = np.array([2, line_1[1]])
        b1 = np.array([1, line_2[0]])
        b2 = np.array([2, line_2[1]])

        da = a2-a1
        db = b2-b1
        dp = a1-b1
        dap = self.perp(da)
        denom = dot( dap, db)
        num = dot( dap, dp )

        return ((num / denom.astype(float))*db + b1)[1]

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

    def _isEquilibriumZone(self, index):
        actual_value = self.ichimoku_dataframe['KIJUN'].iloc[len(self.ichimoku_dataframe['KIJUN'].index) - index];
        value_at_6 = self.ichimoku_dataframe['KIJUN'].iloc[len(self.ichimoku_dataframe['KIJUN'].index) - index - 6];

        if actual_value == value_at_6:
            return True;
        else:
            return False;

    def _isCandleInAValidPosition(self, candle, cross_value):
        if cross_value == 1:
            if self._isPriceTopOfKumo(candle['high']) == True and self._isPriceTopOfKumo(candle['low']) == True:
                return True;
            else:
                return False;
        else:
            if self._isPriceBottomOfKumo(candle['high']) == True and self._isPriceBottomOfKumo(candle['low']) == True:
                return True;
            else:
                return False;

    def _calculateMidPoint(self, high_prices, low_prices, window):
        maxHigh = high_prices.rolling(window=window,center=False).max();
        maxLow = low_prices.rolling(window=window,center=False).min();
        midPoint = (maxHigh + maxLow) / 2;
        return midPoint;

    def CheckPartialClose(self, trade_type, instrument, initial_units, pip_location, actual_value):
        pip_value = self.apiData.GetPipValue(instrument, initial_units, pip_location);

        if pip_value == 0:
            return False;

        actual_pip_value = actual_value / pip_value;

        if actual_pip_value >= 15:
            return True;

        return False;

    def CheckTotalClose(self, trade_type, instrument, last_candle):
        actual_price = self.apiData.GetActualPrice(instrument);
        self._calculateIchimokuLines(instrument, actual_price);

        if trade_type == 1:
            if self.ichimoku_dataframe['TENKAN'].iloc[len(self.ichimoku_dataframe['TENKAN'].index) - 1] < float(last_candle['open']):
                if self.ichimoku_dataframe['TENKAN'].iloc[len(self.ichimoku_dataframe['TENKAN'].index) - 1] < float(last_candle['close']):
                    return True;
        else:
            if self.ichimoku_dataframe['TENKAN'].iloc[len(self.ichimoku_dataframe['TENKAN'].index) - 1] > float(last_candle['open']):
                if self.ichimoku_dataframe['TENKAN'].iloc[len(self.ichimoku_dataframe['TENKAN'].index) - 1] > float(last_candle['close']):
                    return True;

        return False;
