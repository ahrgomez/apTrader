from lib.InstrumentsManager import InstrumentsManager
from lib.ApiData import ApiData
import operator

def main():
    instrumentsManager = InstrumentsManager();
    apiData = ApiData();

    instrumentsManager.GetTradeableInstruments();

    pips = {}

    for inst in instrumentsManager.instruments:
        try:
            pip_value = apiData.GetPipValue(inst, 50, instrumentsManager.instruments[inst]['pipLocation']);
            pips[inst] = pip_value;
        except:
            pass;

    pips_sorted = sorted(pips.items(), key=operator.itemgetter(1))
    i = 0;
    for inst in pips_sorted:
        print inst
        i = i + 1;

if __name__ == "__main__":
    main()
