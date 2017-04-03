from lib.ApiData import ApiData
from lib.InstrumentsManager import InstrumentsManager

from strategies import Ichimoku

from datetime import datetime

access_token = '362c69e15045ab046662317d02837de5-abe03f3f1c7b18419930866fe2bd69b0'
account_id = '101-004-5177797-001'

apiData = ApiData()
instrumentsManager = InstrumentsManager.InstrumentsManager({}, account_id, access_token)

ichimoku = Ichimoku.Ichimoku(account_id, access_token)

def main():
    instrumentsManager.GetTradeableInstruments();
    #instrument = "USD_SAR"
    #print apiData.GetUnitsForPrice(12.9057, instrument, instrumentsManager.instruments[instrument]['precision'], instrumentsManager.instruments[instrument]['rate']);

    #print ichimoku.CheckPartialClose(-1, 'EUR_NZD', 1.52793, 5.02);
    #apiData.CloseTradePartially(trade, 0.5);
    #apiData.ModifyStopLoss(trade['stopLossOrder']['id'], trade['id'], trade['price']);
    #PutOrder(1, 'EUR_HKD', 8.273825, '8.329595')
if __name__ == "__main__":
    main()
