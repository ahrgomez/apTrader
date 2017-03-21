import numpy as np

class SimpleMobileAverage(object):

    smoothing = 0

    def __init__(self, smoothing):
        self.smoothing = smoothing

    def Calculate(self, values):
    	weights = np.repeat(1.0, self.smoothing) / self.smoothing
        return np.convolve(values, weights, 'valid')