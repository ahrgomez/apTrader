
from lib import ApiData, InstrumentsManager
from dateutil import parser
from datetime import datetime

access_token = '362c69e15045ab046662317d02837de5-abe03f3f1c7b18419930866fe2bd69b0'
account_id = '101-004-5177797-001'

apiData = ApiData.ApiData(account_id, access_token)
instrumentsManager = InstrumentsManager.InstrumentsManager({}, account_id, access_token)

def main():
	negative = 0.0;
	positive = 0.0;
	for trade in apiData.GetClosedTrades():
		datetime_object = parser.parse(trade['openTime']);
		print "DT: " + str(datetime_object.date())
		print "DN: "d + str(atetime.today().date())
		if(datetime_object.date() < datetime.today().date()):
			return;

		value = float(trade['realizedPL']);
		if(value < 0):
			negative = negative - value;
		else:
			positive = positive + value;

	print "Negative: " + str(negative);
	print "----"
	print "Positive: " + str(positive);
	print "----"
	print "Total: " + str(positive - negative);
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
