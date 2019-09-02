from lib.ApiData import ApiData

from datetime import datetime
from numpy import *
import numpy as np
import pandas as pd
from lib import Rsi

from math import atan2, degrees, pi
#import matplotlib.pyplot as plt

class Ichimoku(object):

    apiData = {}
    ichimoku_dataframe = pd.DataFrame()
    granularity = "M5"

    def __init__(self, granularity):
        self.apiData = ApiData()
        self.granularity = granularity

    def Verify(self, instrument, candles = None):
        self.ichimoku_dataframe = pd.DataFrame()
        candles = self._calculateIchimokuLines(instrument, candles)

        last_candle, last_candle_index = self.apiData.GetLastClosedCandle(instrument, self.granularity, candles);

        previous_two_candles = candles.tail(2)
        previous_two_candles = previous_two_candles.drop(previous_two_candles.index[len(previous_two_candles)-1])

        rsi = Rsi.Rsi(14)
        rsi_value = rsi.CalculateWithTaLib(candles['close'])[0] + 0.30

        entry_type, entry_price = self._strategy(previous_two_candles, last_candle, rsi_value)

        if entry_type is not None:

            last_candles = candles.tail(20)
            if entry_type == 1:
                stop_loss_price = last_candles['low'].min()
            elif entry_type == -1:
                stop_loss_price = last_candles['high'].max()

            return entry_type, entry_price, stop_loss_price, last_candle['time']

        return None, -1, -1, last_candle['time']

    def _strategy(self, previous_two_candles, last_candle, rsi_value):
        previous_candle = previous_two_candles.iloc[0]

        last_tenkan = self.ichimoku_dataframe['TENKAN'].iloc[len(self.ichimoku_dataframe['TENKAN'].index) - 1]
        last_kinjun = self.ichimoku_dataframe['KIJUN'].iloc[len(self.ichimoku_dataframe['KIJUN'].index) - 1]

        if self._isPriceTopOfKumo(last_tenkan) and self._isPriceTopOfKumo(last_kinjun) and last_tenkan > last_kinjun and self._isCandleInAValidPosition(last_candle, 1):
            #last_invalid_position = self._getLastInvalidLinesPosition(1)
            if rsi_value > 70:
                entry_price = last_candle['close']  # + ((last_candle['close'] - last_candle['open']) / 2)
                return 1, entry_price
        elif self._isPriceBottomOfKumo(last_tenkan) and self._isPriceBottomOfKumo(last_kinjun) and last_kinjun > last_tenkan and self._isCandleInAValidPosition(last_candle, -1):
            #last_invalid_position = self._getLastInvalidLinesPosition(-1)
            if rsi_value < 30:
                entry_price = last_candle['close']  # + ((last_candle['close'] - last_candle['open']) / 2)
                return -1, entry_price

        return None, -1

    def _getLastInvalidLinesPosition(self, type):
        lines_position = -1

        while True:
            last_tenkan = self.ichimoku_dataframe['TENKAN'].iloc[
                len(self.ichimoku_dataframe['TENKAN'].index) + lines_position]
            last_kinjun = self.ichimoku_dataframe['KIJUN'].iloc[
                len(self.ichimoku_dataframe['KIJUN'].index) + lines_position]

            if type == 1:
                if not self._isPriceTopOfKumo(last_tenkan) or not self._isPriceTopOfKumo(last_kinjun):
                    return lines_position
                else:
                    lines_position = lines_position - 1
            elif type == -1:
                if not self._isPriceBottomOfKumo(last_tenkan) or not self._isPriceBottomOfKumo(last_kinjun):
                    return lines_position
                else:
                    lines_position = lines_position - 1

    def _calculateIchimokuLines(self, instrument, data = None, actual_price = None):
        if data is None:
            data = self.apiData.GetData(instrument, self.granularity, 500);

        data = data.drop(data.index[len(data)-1]);

        if actual_price is not None:
            data = data.append({ 'time': datetime.now(),
        			'high': actual_price,
        			'low': actual_price,
        			'close': actual_price}, ignore_index=True)


        self.ichimoku_dataframe['TENKAN'] = self._calculateMidPoint(data['high'], data['low'], 9);
        self.ichimoku_dataframe['KIJUN'] = self._calculateMidPoint(data['high'], data['low'], 26);
        self.ichimoku_dataframe['SENKOU_A'] = ((self.ichimoku_dataframe['TENKAN'] + self.ichimoku_dataframe['KIJUN']) / 2).shift(26);
        self.ichimoku_dataframe['SENKOU_B'] = self._calculateMidPoint(data['high'], data['low'], 52).shift(26);
        self.ichimoku_dataframe['CHIKOU'] = data['close'].shift(-26);
        self.ichimoku_dataframe['PRICE'] = data['close'];

        return data

    def _getCandlePositionFromKumo(self, candle):

        senkou_a = self.ichimoku_dataframe['SENKOU_A'].iloc[len(self.ichimoku_dataframe['SENKOU_A'].index) - 1]
        senkou_b = self.ichimoku_dataframe['SENKOU_B'].iloc[len(self.ichimoku_dataframe['SENKOU_B'].index) - 1]

        if candle['high'] > senkou_a and candle['high'] > senkou_b and candle['low'] > senkou_a and candle['low'] > senkou_b:
            return 1
        elif candle['high'] < senkou_a and candle['high'] < senkou_b and candle['low'] < senkou_a and candle['low'] < senkou_b:
            return -1
        else:
            return 0

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

    def _candleIsCrossing(self, candle, point):

        if point > candle['open'] and point < candle['close']:
            return 1
        elif point < candle['open'] and point > candle['close']:
            return -1
        else:
            return 0

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
        value_at_3 = self.ichimoku_dataframe['KIJUN'].iloc[len(self.ichimoku_dataframe['KIJUN'].index) - index - 3];

        if actual_value == value_at_3:
            return True;
        else:
            return False;

    def _calculateTenkanDegrees(self, instrument):
        self._calculateIchimokuLines(instrument);

        dataS5 = self.apiData.GetData(instrument, self.granularity, 500);
        dataS5 = dataS5.drop(dataS5.index[len(dataS5)-1]);

        actual_price = self.apiData.GetActualPrice(instrument, self.granularity);

        dataS5 = dataS5.append({ 'time': datetime.now(),
    			'high': actual_price,
    			'low': actual_price,
    			'close': actual_price}, ignore_index=True)

        tenkan_aux = self._calculateMidPoint(dataS5['high'], dataS5['low'], 22);

        last_tenkan = self.ichimoku_dataframe['KIJUN'].iloc[len(self.ichimoku_dataframe['KIJUN'].index) - 200];
        actual_tenkan = tenkan_aux.iloc[len(tenkan_aux.index) - 1];

        dx = actual_tenkan - last_tenkan
        dy = actual_tenkan - last_tenkan
        rads = atan2(last_tenkan, actual_tenkan)
        degs = degrees(rads)

        if degs > 45.0:
            degs = degs - 45.0;
            degs = degs * 100.0;
        elif degs < 45.0:
            degs = 45.0 - degs;
            degs = degs * 100;
        else:
            degs = 0;

        return degs;

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

    def CheckPartialClose(self, trade_type, instrument, granularity, initial_units, pip_location, actual_value, target_pip_value):
        pip_value = self.apiData.GetPipValue(instrument, initial_units, pip_location, granularity);

        if pip_value == 0:
            return False;

        actual_pip_value = actual_value / pip_value;

        if actual_pip_value >= target_pip_value:
            return True;

        return False;

    def CheckIsFalseSignal(self, instrument, trade_type):
        self._calculateIchimokuLines(instrument, None)

        last_tenkan = self.ichimoku_dataframe['TENKAN'].iloc[len(self.ichimoku_dataframe['TENKAN'].index) - 2]
        last_kinjun = self.ichimoku_dataframe['KIJUN'].iloc[len(self.ichimoku_dataframe['KIJUN'].index) - 2]

        if trade_type == 1:
            return last_kinjun >= last_tenkan
        elif trade_type == -1:
            return last_tenkan >= last_kinjun
        else:
            return False

    def CheckTotalClose(self, trade_type, instrument, last_candle):
        actual_price = self.apiData.GetActualPrice(instrument, self.granularity);
        self._calculateIchimokuLines(instrument, None, actual_price);

        if trade_type == 1:
            if self.ichimoku_dataframe['TENKAN'].iloc[len(self.ichimoku_dataframe['TENKAN'].index) - 2] > float(last_candle['open']):
                if self.ichimoku_dataframe['TENKAN'].iloc[len(self.ichimoku_dataframe['TENKAN'].index) - 2] > float(last_candle['close']):
                    return True;
        else:
            if self.ichimoku_dataframe['TENKAN'].iloc[len(self.ichimoku_dataframe['TENKAN'].index) - 2] < float(last_candle['open']):
                if self.ichimoku_dataframe['TENKAN'].iloc[len(self.ichimoku_dataframe['TENKAN'].index) - 2] < float(last_candle['close']):
                    return True;

        return False;
