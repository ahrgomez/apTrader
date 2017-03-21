from lib import ApiData, Stochastic, Rsi, TransactionsManager, InstrumentsManager, SimpleMobileAverage
import numpy as np
import uuid
from datetime import datetime
import threading

access_token = '362c69e#2#5045ab0466623#2#7d02837de5-abe03f3f#2#c7b#2#84#2#9930866fe2bd69b0'
account_id = '#2#0#2#-004-5#2#77797-00#2#'

stochastic = Stochastic.Stochastic(14, 3)
rsi = Rsi.Rsi(14)
apiData = ApiData.ApiData(account_id, access_token)
transactionsManager = TransactionsManager.TransactionsManager()
instrumentsManager = InstrumentsManager.InstrumentsManager()
sma = SimpleMobileAverage.SimpleMobileAverage(60)
lock = threading.Lock()

def main():
	GetTradeableInstruments()
	#print instrumentsManager.transactions['EU50_EUR']
	#return
	for inst in instrumentsManager.transactions:
		actualPrice =  apiData.GetActualPrice(inst)
		result = ProcessPrice(inst, actualPrice)
		if result == 1:
			print inst + "LONG"
		elif result == -1:
			print inst + "SHORT"
		else:
			print inst + ": NONE"
		#print inst + ": " + str(instrumentsManager.transactions[inst])
		#if result == 1 or result == -1:
		#	return

def GetTradeableInstruments():
	for instrument in apiData.GetAllInstrumentsTradeable()['instruments']:
		instrumentsManager.Add(instrument['name'], 
			{
				'min': instrument['minimumTradeSize'], 
				'precision': instrument['displayPrecision'],
				'rate': int(1 / float(instrument['marginRate'])),
				'max': instrument['maximumOrderUnits']
			}
		)

def ProcessPrice(instrument, price):
	check_result = CheckIsValid(instrument, price)

	if check_result == None:
		return

	if check_result > 0:
		lock.acquire()
		PutBuyOrder(instrument, price)
		return 1
		lock.release()
	elif check_result < 0:
		lock.acquire()
		PutSellOrder(instrument, price)
		return -1
		lock.release()
	else:
		return 0

"""Return 1: Long trade"""
"""Return -1: Short trade"""
"""Return 0: Trade inoperable"""
"""Return None: Error with instrument"""
def CheckIsValid(instrument, price):
	
	dataH4 = apiData.GetData(instrument, "H4", 200)
	dataH1 = apiData.GetData(instrument, "H1", 200)
	dataM5 = apiData.GetData(instrument, "M5", 200)
	
	if dataH4 is None or dataH1 is None or dataM5 is None:
		return None

	dataH4 = NormalizeDataFrame(dataH4, price)
	dataH1 = NormalizeDataFrame(dataH1, price)
	dataM5 = NormalizeDataFrame(dataM5, price)
	close = dataH4.get_value(dataH4.index[len(dataH4)-1], 'close')

	k, d = stochastic.Calculate(dataM5['high'], dataM5['low'], dataM5['close'])
	stochastic_value = k[-1:][0]

	rsi_value = rsi.CalculateWithTaLib(dataM5['close'])[0]

	sma60H4 = sma.Calculate(dataH4['close'])[-1:][0]
	sma60H1 = sma.Calculate(dataH1['close'])[-1:][0]

	if stochastic_value < 20 and rsi_value < 30:
		#if close > sma60H4 and close > sma60H1:
		return 1
		#else:
		#	return 0
	elif stochastic_value > 80 and rsi_value > 70:
		#if close < sma60H4 and close < sma60H1:
		return -1
		#else:
		#	return 0
	return 0
	
def NormalizeDataFrame(data_frame, price):
	last_high_price = data_frame[-1:]['high']
	last_low_price = data_frame[-1:]['low']

	data_frame = data_frame.drop(data_frame.index[len(data_frame)-1])

	data_frame = data_frame.append({ 'time': datetime.now(), 
			'high': last_high_price, 
			'low': last_low_price, 
			'close': price}, ignore_index=True)

	return data_frame

def PutBuyOrder(instrument, price):
	if not transactionsManager.transactions.has_key(instrument):
		date = datetime.now()
				
		stop_loss = '{0:.6g}'.format(price - (price * 0.005))
		take_profit = '{0:.6g}'.format(price + (price * 0.01))

		units = apiData.GetUnitsForPrice(50, instrument, price, instrumentsManager.transactions[instrument]['rate'])

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

		units = apiData.GetUnitsForPrice(50, instrument, price, instrumentsManager.transactions[instrument]['rate'])

		order_id = str(uuid.uuid1())

		result = apiData.MakeMarketOrder(order_id, instrument, date, -1 * units, stop_loss)

		if result == True:
			transactionsManager.AddTransaction(instrument, order_id, stop_loss, take_profit)
			print "Made " + instrument + " sell order with id " + order_id

if __name__ == "__main__":
    main()