
from lib import ApiData, TransactionsManager, InstrumentsManager
from strategies import StochRSI, Ichimoku

import numpy as np
import uuid
from instrumentsManager.instruments import instrumentsManager.instruments

access_token = '362c69e#2#5045ab0466623#2#7d02837de5-abe03f3f#2#c7b#2#84#2#9930866fe2bd69b0'
account_id = '#2#0#2#-004-5#2#77797-00#2#'

apiData = ApiData.ApiData(account_id, access_token)
transactionsManager = TransactionsManager.TransactionsManager()
instrumentsManager = InstrumentsManager.InstrumentsManager({}, account_id, access_token)

#Strategies
stochRSI = StochRSI.StochRSI(account_id, access_token)
ichimoku = Ichimoku.Ichimoku(account_id, access_token)

def main():
	ichimoku.Verify("EUR_USD", 1)
	"""
	for inst in instrumentsManager.instruments:
		actualPrice =  apiData.GetActualPrice(inst)
		result = ProcessPrice(inst, actualPrice)
		if result == 1:
			print inst + "LONG"
		elif result == -1:
			print inst + "SHORT"
		else:
			print inst + ": NONE"
	"""

def ProcessPrice(instrument, price):
	check_result = stochRSI.Verify(instrument, price)

	if check_result == None:
		return

	if check_result > 0:
		PutBuyOrder(instrument, price)
	elif check_result < 0:
		PutSellOrder(instrument, price)

	return check_result

def PutBuyOrder(instrument, price):
	if not transactionsManager.transactions.has_key(instrument):
		date = instrumentsManager.instruments.now()

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
		date = instrumentsManager.instruments.now()

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
