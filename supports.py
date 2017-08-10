from lib.ApiData import ApiData
from scipy.signal import savgol_filter as smooth
import numpy as np
import warnings
warnings.filterwarnings(action="ignore", module="scipy", message="^internal gelsd")

apiData = ApiData()

RANGE_LENGTH = 10
RANGE_VALUE = 0.010

def main():
    yearData = apiData.GetData("USD_JPY", "D", 670);
    ranges = getRanges(yearData[:670]["low"])
    minValues = getRangesMinValues(ranges)

    supports = []
    while(len(minValues) > 0):
        minOfMinValues = np.amin(minValues)
        points, minValues = calculateSupportPointsArrayAndStrength(minValues, minOfMinValues)
        supports.append([len(points), minOfMinValues])

    print supports

def getRanges(data):
    chunks = [data[x:x+RANGE_LENGTH] for x in xrange(0, len(data), RANGE_LENGTH)]
    return chunks

def getRangesMinValues(ranges):
    minValues = []
    for x in xrange(0, len(ranges), 1):
        range = ranges[x]
        min = np.amin(range)
        minValues.append(min);
    return minValues

def calculateSupportPointsArrayAndStrength(minValues, minOfMinValues):
    supportPointsArray = [minOfMinValues]
    minValues.remove(minOfMinValues);
    inRangeValue = minOfMinValues * RANGE_VALUE
    minRangeValue = minOfMinValues - inRangeValue
    maxRangeValue = minOfMinValues + inRangeValue

    for x in xrange(0, len(minValues), 1):
        val = minValues[x]

        if val > minRangeValue and val < maxRangeValue:
            supportPointsArray.append(val)

    for x in xrange(0, len(supportPointsArray), 1):
        val = supportPointsArray[x]

        if val in minValues:
            minValues.remove(val)

    return supportPointsArray, minValues

if __name__ == "__main__":
        main()
