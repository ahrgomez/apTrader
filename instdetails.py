from lib.ApiData import ApiData
from lib.InstrumentsManager import InstrumentsManager

apiData = ApiData()
instrumentsManager = InstrumentsManager({})

def main():
    instrumentsManager.GetTradeableInstruments();
    instrument = "EUR_ZAR"

    print instrumentsManager.instruments[instrument]

if __name__ == "__main__":
    main()
