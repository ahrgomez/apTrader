
from lib import ApiData, TransactionsManager, InstrumentsManager
from strategies import StochRSI, Ichimoku

import numpy as np
import uuid
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
	inst = "GBP_USD"
	#for inst in instrumentsManager.instruments:
	actualPrice =  apiData.GetActualPrice(inst)
	result = ProcessPrice(inst, actualPrice)
	if result == 1:
		print inst + "LONG"
	elif result == -1:
		print inst + "SHORT"
	else:
		print inst + ": NONE"


def ProcessPrice(instrument, price):
	check_result = ichimoku.Verify(instrument, price)

	if check_result == None:
		return

	if check_result > 0:
		PutBuyOrder(instrument, price)
	elif check_result < 0:
		PutSellOrder(instrument, price)

	return check_result

def PutBuyOrder(instrument, price):
	if not transactionsManager.transactions.has_key(instrument):
		date = datetime.now()

		stop_loss = '{0:.6g}'.format(price - (price * 0.005))
		take_profit = '{0:.6g}'.format(price + (price * 0.01))

		units = apiData.GetUnitsForPrice(50, instrument, price, instrumentsManager.instruments[instrument]['rate'])

		order_id = str(uuid.uuid1())

		result = apiData.MakeMarketOrder(order_id, instrument, date, units, stop_loss)

		if result == True:
			transactionsManager.AddTransaction(instrument, order_id, stop_loss, take_profit)
			print "Made " + instrument + " buy order with id " + order_id

def PutSellOrder(instrument, price):
	if not transactionsManager.transactions.has_key(instrument):
		date = datetime.now()

		stop_loss = '{0:.6g}'.format(price + (price * 0.005))
		take_profit = '{0:.6g}'.format(price - (price * 0.01))

		units = apiData.GetUnitsForPrice(50, instrument, price, instrumentsManager.instruments[instrument]['rate'])

		order_id = str(uuid.uuid1())

		result = apiData.MakeMarketOrder(order_id, instrument, date, -1 * units, stop_loss)

		if result == True:
			transactionsManager.AddTransaction(instrument, order_id, stop_loss, take_profit)
			print "Made " + instrument + " sell order with id " + order_id

if __name__ == "__main__":
    main()
