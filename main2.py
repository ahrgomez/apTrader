from lib import ApiData, Stochastic, Rsi
import numpy as np
from datetime import datetime

def main():
	access_token = '4b235e85b436ca865f04e54bdd4c7849-a9760d399f950d764431f65e8f4e40d6'
	account_id = '101-004-5177797-001'

	stochastic = Stochastic.Stochastic(14, 3)
	rsi = Rsi.Rsi(14)
	apiData = ApiData.ApiData(account_id, access_token)

	for response in apiData.GetStreamingData("EUR_USD,GBP_USD,EUR_GBP"):
		
		instrument = response['instrument']
		price = response['price']

		data = apiData.GetData(instrument, "H1", 20)
		
		last_high_price = data[-1:]['high']
		last_low_price = data[-1:]['low']

		data = data.drop(data.index[len(data)-1])

		data = data.append({ 'time': datetime.now(), 
				'high': last_high_price, 
				'low': last_low_price, 
				'close': price}, ignore_index=True)

		k, d = stochastic.Calculate(data['high'], data['low'], data['close'])

		rsi_value = rsi.Calculate(data['close'])

		print "Instrument: " + instrument
		print "Actual price: " + str(price)
		print "Slow Stochastic: " + str(d[-1:][0])
		print "RSI: " + str(rsi_value)
		print ""

if __name__ == "__main__":
    main()