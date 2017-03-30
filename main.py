
from lib import ApiData, TransactionsManager, InstrumentsManager
from strategies import StochRSI, Ichimoku

import numpy as np
import uuid
import json
from datetime import datetime

access_token = '362c69e15045ab046662317d02837de5-abe03f3f1c7b18419930866fe2bd69b0'
account_id = '101-004-5177797-001'

apiData = ApiData.ApiData(account_id, access_token)
transactionsManager = TransactionsManager.TransactionsManager()
instrumentsManager = InstrumentsManager.InstrumentsManager({}, account_id, access_token)

#Strategies
stochRSI = StochRSI.StochRSI(account_id, access_token)
ichimoku = Ichimoku.Ichimoku(account_id, access_token)

def main():
	instruments_list = "";
	instrumentsManager.GetTradeableInstruments();
	for inst in instrumentsManager.instruments:
		instruments_list +=  inst + ",";

	while(True):
		try:
			for tick in apiData.GetStreamingData(instruments_list):
				instrument = tick['instrument'];
				price = tick['price'];

				result = ProcessPrice(instrument, price);

				if result is None:
					print instrument + ": " + "NONE"
				elif result == 1:
					print instrument + ": " + "LONG"
				else:
					print instrument + ": " + "SHORT"
		except:
			pass;

def ProcessPrice(instrument, price):
	check_result, stop_loss_price = ichimoku.Verify(instrument, price)

	if check_result is None:
		return

	PutOrder(check_result, instrument, price, stop_loss_price);

	return check_result

def PutOrder(order_type, instrument, price, stop_loss):
	if not transactionsManager.transactions.has_key(instrument):
		date = datetime.now()
		units = apiData.GetUnitsForPrice(50, instrument, instrumentsManager.instruments[instrument]['rate']);

		if units is None:
			print "Can't have units to " + instrument
			return None;

		order_id = str(uuid.uuid1())

		stop_loss = '{0:.6g}'.format(stop_loss)
		result = apiData.MakeMarketOrder(order_id, instrument, date, order_type * units, stop_loss)

		if result == True:
			transactionsManager.AddTransaction(instrument, order_id, stop_loss)
			print "Made " + instrument + " order with id " + order_id + " with " + str(order_type * units) + " units"

if __name__ == "__main__":
    main()
