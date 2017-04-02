
from lib import ApiData, InstrumentsManager
from strategies import Ichimoku
from raven import Client

import numpy as np
import uuid
import json
from datetime import datetime
from time import sleep

access_token = '362c69e15045ab046662317d02837de5-abe03f3f1c7b18419930866fe2bd69b0'
account_id = '101-004-5177797-001'

apiData = ApiData.ApiData(account_id, access_token)
instrumentsManager = InstrumentsManager.InstrumentsManager({}, account_id, access_token)
errorsManagement = Client('https://7932a7da676c4962895957059416bd7d:da9a1669ee724bb2b61cf7b47b430ccc@sentry.io/154029')

#Strategies
ichimoku = Ichimoku.Ichimoku(account_id, access_token)

def main():
	instruments_list = "";
	instrumentsManager.GetTradeableInstruments();
	for inst in instrumentsManager.instruments:
		instruments_list +=  inst + ",";

	while(True):
		try:
			if IsForbiddenTime():
				print "BOLSA CERRADA";
				sleep(60);
				continue;

			for tick in apiData.GetStreamingData(instruments_list):
				if IsForbiddenTime():
					print "BOLSA CERRADA";
					sleep(60);
					break;

				instrument = tick['instrument'];
				price = tick['price'];

				instrument_part_A = instrument.split('_')[0];
				instrument_part_A = instrument_part_A.encode('ascii','ignore');
				instrument_part_B = instrument.split('_')[1];
				instrument_part_B = instrument_part_B.encode('ascii','ignore');

				instrument = instrument_part_A + '_' + instrument_part_B;

				result = ProcessPrice(instrument, price);

				if result is None:
					print instrument + ": " + "NONE"
				elif result == 1:
					print instrument + ": " + "LONG"
				else:
					print instrument + ": " + "SHORT"
		except KeyboardInterrupt:
			break;
		except:
			errorsManagement.captureException();
			pass;

def ProcessPrice(instrument, price):
	check_result, stop_loss_price = ichimoku.Verify(instrument, price)

	if check_result is None:
		return

	if PutOrder(check_result, instrument, price, stop_loss_price):
		return check_result;
	else:
		return None;

def PutOrder(order_type, instrument, price, stop_loss):
	if not apiData.ExistsTradeOfInstrument(instrument):
		date = datetime.now()
		units = apiData.GetUnitsForPrice(50, instrument, instrumentsManager.instruments[instrument]['precision'], instrumentsManager.instruments[instrument]['rate']);

		if units is None:
			print "Can't have units to " + instrument
			return None;

		order_id = str(uuid.uuid1())

		stop_loss = '{0:.6g}'.format(stop_loss)

		total_units = order_type * float(units);

		result = apiData.MakeMarketOrder(order_id, instrument, date, total_units, stop_loss)

		if result == True:
			print "Made " + instrument + " order with id " + order_id + " with " + str(order_type * units) + " units"
			return True;

		return False;

def IsForbiddenTime():
	weekday = datetime.today().weekday();
	today = datetime.today();

	if weekday == 4 and today.hour > 21:
		return True;

	if weekday == 5:
		return True;

	if weekday == 6 and today.hour < 21:
		return True;

	return False;

if __name__ == "__main__":
    main()
