
from lib import ApiData, InstrumentsManager

access_token = '362c69e15045ab046662317d02837de5-abe03f3f1c7b18419930866fe2bd69b0'
account_id = '101-004-5177797-001'

apiData = ApiData.ApiData(account_id, access_token)
instrumentsManager = InstrumentsManager.InstrumentsManager({}, account_id, access_token)

def main():
	apiData.GetClosedTrades();
	#trades = apiData.GetTradesOpened()
	#for trade in trades:
	#	if trade['instrument'] == 'EUR_GBP':
	#		apiData.ModifyStopLoss(trade['stopLossOrder']['id'], trade['id'], trade['price']);
	#instrumentsManager.GetTradeableInstruments();
	#GetTradeableInstruments()
	#for inst in instrumentsManager.transactions:
	#	print inst + ": " + str(instrumentsManager.transactions[inst])

def GetTradeableInstruments():
	for instrument in apiData.GetAllInstrumentsTradeable()['instruments']:
		print instrument;
		print instrumentsManager.instruments[instruments];

if __name__ == "__main__":
    main()
