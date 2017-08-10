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
    ranges = getRanges(yearData[:670]["high"])
    maxValues = getRangesMaxValues(ranges)

    resistences = []
    while(len(maxValues) > 0):
        maxOfMaxValues = np.amax(maxValues)
        points, maxValues = calculateResistencePointsArrayAndStrength(maxValues, maxOfMaxValues)
        resistences.append([len(points), maxOfMaxValues])

    print resistences

def getRanges(data):
    chunks = [data[x:x+RANGE_LENGTH] for x in xrange(0, len(data), RANGE_LENGTH)]
    return chunks

def getRangesMaxValues(ranges):
    maxValues = []
    for x in xrange(0, len(ranges), 1):
        range = ranges[x]
        max = np.amax(range)
        maxValues.append(max);
    return maxValues

def calculateResistencePointsArrayAndStrength(maxValues, maxOfMaxValues):
    resistencePointsArray = [maxOfMaxValues]
    maxValues.remove(maxOfMaxValues);
    inRangeValue = maxOfMaxValues * RANGE_VALUE
    minRangeValue = maxOfMaxValues - inRangeValue
    maxRangeValue = maxOfMaxValues + inRangeValue

    for x in xrange(0, len(maxValues), 1):
        val = maxValues[x]

        if val > minRangeValue and val < maxRangeValue:
            resistencePointsArray.append(val)

    for x in xrange(0, len(resistencePointsArray), 1):
        val = resistencePointsArray[x]

        if val in maxValues:
            maxValues.remove(val)

    return resistencePointsArray, maxValues

if __name__ == "__main__":
        main()
