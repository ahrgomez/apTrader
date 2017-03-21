import pandas as pd
import numpy as np
import SimpleMobileAverage

class Stochastic(object):

    periods = 0
    smoothing = 0
    sma = None

    def __init__(self, period, smoothing):
        self.periods = period
        self.smoothing = smoothing
        self.sma = SimpleMobileAverage.SimpleMobileAverage(smoothing)

    def Calculate(self, high_prices, low_prices, close_prices):

        return self.getSlowStochastic(low_prices, high_prices, close_prices)

    def getFastStochastic(self, low_prices, high_prices, close_prices):
        low_min = low_prices.rolling(window=self.periods,center=False).min()
        high_max = high_prices.rolling(window=self.periods,center=False).max()

        k_fast = 100 * (close_prices - low_min)/(high_max - low_min)
        k_fast = k_fast.dropna()
        d_fast = self.sma.Calculate(k_fast)
        return k_fast, d_fast


    def getSlowStochastic(self, low_prices, high_prices, close_prices):
        k_fast, d_fast = self.getFastStochastic(low_prices, high_prices, close_prices)
        k_slow = d_fast
        d_slow = self.sma.Calculate(k_slow)
        return k_slow, d_slow
