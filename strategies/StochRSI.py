from lib import ApiData, Stochastic, Rsi, SimpleMobileAverage

from datetime import datetime
import numpy as np

class StochRSI(object):

    stochastic = {}
    rsi = {}
    apiData = {}
    sma = {}

    def __init__(self, api_account_id, api_access_token):
        self.apiData = ApiData()
        self.rsi = Rsi.Rsi(14)
        self.stochastic = Stochastic.Stochastic(14, 3)
        self.sma = SimpleMobileAverage.SimpleMobileAverage(60)

    """Return 1: Long trade"""
    """Return -1: Short trade"""
    """Return 0: Trade inoperable"""
    """Return None: Error with instrument"""
    def Verify(self, instrument, actual_price):
        dataH4 = self.apiData.GetData(instrument, "H4", 200)
    	dataH1 = self.apiData.GetData(instrument, "H1", 200)
    	dataM5 = self.apiData.GetData(instrument, "M5", 200)

    	if dataH4 is None or dataH1 is None or dataM5 is None:
    		return None

    	dataH4 = self.NormalizeDataFrame(dataH4, actual_price)
    	dataH1 = self.NormalizeDataFrame(dataH1, actual_price)
    	dataM5 = self.NormalizeDataFrame(dataM5, actual_price)
    	close = dataH4.get_value(dataH4.index[len(dataH4)-1], 'close')

    	k, d = self.stochastic.Calculate(dataM5['high'], dataM5['low'], dataM5['close'])
    	stochastic_value = k[-1:][0]

    	rsi_value = self.rsi.CalculateWithTaLib(dataM5['close'])[0]

    	sma60H4 = self.sma.Calculate(dataH4['close'])[-1:][0]
    	sma60H1 = self.sma.Calculate(dataH1['close'])[-1:][0]

    	if stochastic_value < 20 and rsi_value < 30:
    		#if close > sma60H4 and close > sma60H1:
    		return 1
    		#else:
    		#	return 0
    	elif stochastic_value > 80 and rsi_value > 70:
    		#if close < sma60H4 and close < sma60H1:
    		return -1
    		#else:
    		#	return 0
    	return 0

    def NormalizeDataFrame(self, data_frame, price):
    	last_high_price = data_frame[-1:]['high']
    	last_low_price = data_frame[-1:]['low']

    	data_frame = data_frame.drop(data_frame.index[len(data_frame)-1])

    	data_frame = data_frame.append({ 'time': datetime.now(),
    			'high': last_high_price,
    			'low': last_low_price,
    			'close': price}, ignore_index=True)

    	return data_frame
