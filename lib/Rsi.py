import pandas as pd
import numpy as np
import talib as ta

class Rsi(object):

    periods = 0

    def __init__(self, period):
        self.periods = period

    def Calculate(self, prices_data_frame):
    	prices_data_frame = prices_data_frame[self.periods * -1:]

    	i = 1;
    	
    	upward_sum = 0
    	downward_sum = 0

    	while(i < self.periods):
    		valueA = prices_data_frame[prices_data_frame.index[i - 1]]
    		valueB = prices_data_frame[prices_data_frame.index[i]]

    		valueA = float('{0:.6g}'.format(valueA))
    		valueB = float('{0:.6g}'.format(valueB))

    		if(valueB > valueA):
    			diffup = float(valueB - valueA)
    			upward_sum+=diffup
    		elif(valueA > valueB):
    			diffdown = float(valueA - valueB)
    			downward_sum+=diffdown
    		i+=1

    	upward_average = upward_sum / self.periods
    	downward_average = downward_sum / self.periods

    	rs = upward_average / downward_average

    	return 100 - (100 / (1 + rs))

    def CalculateWithTaLib(self, prices_data_frame):
        return ta.RSI(prices_data_frame.values, self.periods)[-1:]