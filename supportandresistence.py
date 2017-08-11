from lib.ApiData import ApiData
from scipy.signal import savgol_filter as smooth
import numpy as np
import warnings
warnings.filterwarnings(action="ignore", module="scipy", message="^internal gelsd")
import sys

apiData = ApiData()

RANGE_LENGTH = 10
RANGE_VALUE = 0.010
ELEMENTS_COUNT = 670

def main():
    if len(sys.argv) == 1:
        print("Debe instroducir un instrument")
    else:
        instrument = sys.argv[1]

        yearData = apiData.GetData(str(instrument), "H1", ELEMENTS_COUNT);
        lowRanges = getRanges(yearData[:ELEMENTS_COUNT]["low"])
        highRanges = getRanges(yearData[:ELEMENTS_COUNT]["high"])

        values = []
        values.extend(getRangesMinValues(lowRanges))
        values.extend(getRangesMaxValues(highRanges))

        supportAndResistences = []

        while(len(values) > 0):
            maxOfValues = np.amax(values)
            points, values = calculateResistencePointsArrayAndStrength(values, maxOfValues)
            supportAndResistences.append([len(points), maxOfValues])

        print supportAndResistences




# -----------------------------


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
