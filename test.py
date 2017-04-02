from lib import ApiData, InstrumentsManager

from strategies import Ichimoku

access_token = '362c69e15045ab046662317d02837de5-abe03f3f1c7b18419930866fe2bd69b0'
account_id = '101-004-5177797-001'

apiData = ApiData.ApiData(account_id, access_token)
instrumentsManager = InstrumentsManager.InstrumentsManager({}, account_id, access_token)

ichimoku = Ichimoku.Ichimoku(account_id, access_token)

def main():
    #instrumentsManager.GetTradeableInstruments();
    #instrument = "USD_SAR"
    #print apiData.GetUnitsForPrice(12.9057, instrument, instrumentsManager.instruments[instrument]['precision'], instrumentsManager.instruments[instrument]['rate']);

    #print ichimoku.CheckPartialClose(-1, 'EUR_NZD', 1.52793, 5.02);
    #apiData.CloseTradePartially(trade, 0.5);
    #apiData.ModifyStopLoss(trade['stopLossOrder']['id'], trade['id'], trade['price']);

    print apiData.GetConvertPriceCurrencyWithFixer("USD", "EUR")

if __name__ == "__main__":
    main()
