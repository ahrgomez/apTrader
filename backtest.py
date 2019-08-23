
from lib.ApiData import ApiData
from lib.InstrumentsManager import InstrumentsManager

from api.PricesStream import PricesStream
from api.OrdersData import OrdersData

from strategies import Ichimoku
from raven import Client

import numpy as np
import uuid
import json
from datetime import datetime
from time import sleep


apiData = ApiData()
instrumentsManager = InstrumentsManager({})
errorsManagement = Client('https://7932a7da676c4962895957059416bd7d:da9a1669ee724bb2b61cf7b47b430ccc@sentry.io/154029')

#Strategies
granularity = "M5"
pip_target = 1.25
ichimoku = Ichimoku.Ichimoku(granularity)

trades = {}

DEBUG = True;

def main():

	try:
		instrument = 'EUR_USD'
		candles = apiData.GetData(instrument, granularity, 5000)

		start = 10

		for index, candle in candles.iterrows():

			instrument_part_A = instrument.split('_')[0];
			instrument_part_A = instrument_part_A.encode('ascii', 'ignore');
			instrument_part_B = instrument.split('_')[1];
			instrument_part_B = instrument_part_B.encode('ascii', 'ignore');

			instrument = instrument_part_A + '_' + instrument_part_B;

			actual_candles_array = candles.head(start)

			result = ProcessPrice(instrument, actual_candles_array);
			start = start + 1

			if DEBUG:
				if result == 1:
					print instrument + ": " + "LONG"
				elif result == -1:
					print instrument + ": " + "SHORT"


			if trades.has_key(instrument):
				CheckToCloseTrade(trades[instrument], instrument, actual_candles_array[:-1])
	except KeyboardInterrupt:
		return
	except:
		errorsManagement.captureException();
		pass;

def ProcessPrice(instrument, candles):
	check_result, entry_price, stop_loss_price, time = ichimoku.Verify(instrument, candles)
	if check_result is None:
		return

	if PutOrder(check_result, instrument, time, entry_price, stop_loss_price):
		print time + ": " + str(entry_price) + "/" + str(stop_loss_price)

		return check_result
	else:
		return None

######### SUPERVISOR ZONE ########################

def PutOrder(order_type, instrument, time, entry_price, price, stop_loss):

	if not trades.has_key(instrument):

		units = apiData.GetUnitsForPrice(50, instrument, instrumentsManager.instruments[instrument]['precision'],
										 granularity, instrumentsManager.instruments[instrument]['rate']);

		if units is None or units == 0:
			print "Can't have units to " + instrument
			return None;

		order_id = str(uuid.uuid1())

		i, p, d = str(price).partition('.');
		price_precision = len(d);

		stop_loss = apiData.GetPriceFormatted(stop_loss, instrumentsManager.instruments[instrument]['pricePrecision']);

		total_units = order_type * float(units);

		entry_price = apiData.GetPriceFormatted(entry_price,
												instrumentsManager.instruments[instrument]['pricePrecision']);

		result = False;

		trade = {}
		trade["time"] = time
		trade["type"] = order_type
		trade["entry_price"] = entry_price
		trade["stop_loss"] = stop_loss
		trade["initialUnits"] = total_units
		trades[instrument] = trade

		print "Made " + instrument + " order with id " + order_id + " with " + str(order_type * units) + " units"
		return True

def CheckToCloseTrade(trade, instrument, last_candle):
    if trade.has_key('partially_closed'):
        if CheckTotalClose(instrument, trade['type'], last_candle):
            print instrument + " A CERRAR DEL TODO";
            OrdersData().CloseTradePartially(trade, 0);
        else:
            CheckTraillingStop(trade, trade['type'], last_candle['close']);
    else:
        if CheckPartialClose(trade, instrument, trade['type']):
            print instrument + " A CERRAR A MITAD";
            OrdersData().CloseTradePartially(trade, 0.5);
            OrdersData().ModifyStopLoss(trade['stopLossOrder']['id'], trade['id'], trade['price']);

def CheckTraillingStop(trade, trade_type, actual_price):
    instrument = trade['instrument']
    actual_price = float(apiData.GetActualPrice(instrument, granularity));
    stop_loss_price = float(trade['stopLossOrder']['price']);
    begining_price = float(trade['price']);

    if trade_type == 1:
        if begining_price > stop_loss_price:
            return;
        else:
            last_candle = apiData.GetLastClosedCandle(instrument, granularity)[0]
            if stop_loss_price >= last_candle['low']:
                return;
            else:
                new_stop_loss = last_candle['low'];
    elif trade_type == -1:
        if begining_price < stop_loss_price:
            return;
        else:
            last_candle = apiData.GetLastClosedCandle(instrument, granularity)[0]
            if stop_loss_price <= last_candle['high']:
                return;
            else:
                new_stop_loss = last_candle['high'];

    new_stop_loss = apiData.GetPriceFormatted(new_stop_loss, instrumentsManager.instruments[instrument]['pricePrecision']);

    OrdersData().ModifyStopLoss(trade['stopLossOrder']['id'], trade['id'], str(new_stop_loss));
    print "Upload stop loss from " + instrument + " to " + str(new_stop_loss);

def CheckTotalClose(instrument, trade_type, last_candle):
    if last_candle is None:
        return False;
    else:
        return ichimoku.CheckTotalClose(trade_type, instrument, last_candle)

def CheckPartialClose(trade, instrument, trade_type):
    return ichimoku.CheckPartialClose(trade_type, instrument, granularity, float(trade['initialUnits']), instrumentsManager.instruments[instrument]['pipLocation'], float(trade['unrealizedPL']), pip_target);

##################################################

if __name__ == "__main__":
    main()
