from lib import ApiData, InstrumentsManager

access_token = '362c69e15045ab046662317d02837de5-abe03f3f1c7b18419930866fe2bd69b0'
account_id = '101-004-5177797-001'

apiData = ApiData.ApiData(account_id, access_token)
instrumentsManager = InstrumentsManager.InstrumentsManager({}, account_id, access_token)

def main():
    instrumentsManager.GetTradeableInstruments();
    instrument = "USD_SAR"
    print apiData.GetUnitsForPrice(12.9057, instrument, instrumentsManager.instruments[instrument]['precision'], instrumentsManager.instruments[instrument]['rate']);

if __name__ == "__main__":
    main()
