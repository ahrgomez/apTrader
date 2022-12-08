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

import traceback

apiData = ApiData()
instrumentsManager = InstrumentsManager({})
errorsManagement = Client('https://7932a7da676c4962895957059416bd7d:da9a1669ee724bb2b61cf7b47b430ccc@sentry.io/154029')

# Strategies
granularity = "M30"
pip_target = 10
ichimoku = Ichimoku.Ichimoku(granularity)

TotalPips = 0

trades = {}
actual_candles_array = []
DEBUG = True;


def main():
    try:
        instrument = 'EUR_USD'
        candles = apiData.GetData(instrument, granularity, 5000)
        #candles = apiData.GetBacktestData()
        start = 10

        for index, candle in candles.iterrows():

            instrument_part_A = instrument.split('_')[0];
            instrument_part_A = instrument_part_A.encode('ascii', 'ignore');
            instrument_part_B = instrument.split('_')[1];
            instrument_part_B = instrument_part_B.encode('ascii', 'ignore');

            instrument = instrument_part_A + '_' + instrument_part_B;

            global actual_candles_array

            actual_candles_array = candles.head(start)

            result = ProcessPrice(instrument, actual_candles_array);
            start = start + 1

            if DEBUG:
                if result == 1:
                    print instrument + ": " + "LONG"
                elif result == -1:
                    print instrument + ": " + "SHORT"


            if trades.has_key(instrument):
                CheckToCloseTrade(trades[instrument], instrument, actual_candles_array[-1:])

    except KeyboardInterrupt:
        return
    except Exception, e:
        print "error!"
        traceback.print_exc()
        errorsManagement.captureException()
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

def PutOrder(order_type, instrument, time, entry_price, stop_loss):
    if not trades.has_key(instrument):

        units = apiData.GetUnitsForPrice(50, instrument, instrumentsManager.instruments[instrument]['precision'],
                                         granularity, instrumentsManager.instruments[instrument]['rate']);

        if units is None or units == 0:
            print "Can't have units to " + instrument
            return None;

        order_id = str(uuid.uuid1())

        stop_loss = apiData.GetPriceFormatted(stop_loss, instrumentsManager.instruments[instrument]['pricePrecision']);

        total_units = order_type * float(units);

        entry_price = apiData.GetPriceFormatted(entry_price,
                                                instrumentsManager.instruments[instrument]['pricePrecision']);

        result = False;

        trade = {}
        trade["instrument"] = instrument
        trade["time"] = time
        trade["type"] = order_type
        trade["price"] = entry_price
        trade["stopLossOrder"] = {}
        trade["stopLossOrder"]["price"] = stop_loss
        trade["initialUnits"] = total_units
        trades[instrument] = trade

        print "Made " + instrument + " order with id " + order_id + " with " + str(order_type * units) + " units"
        return True


def CheckToCloseTrade(trade, instrument, last_candle):

    global TotalPips

    if trade['type'] == 1 and (float(last_candle['close']) < float(trade['stopLossOrder']['price']) or float(last_candle['high']) < float(trade['stopLossOrder']['price']) or float(last_candle['low']) < float(trade['stopLossOrder']['price'])):
        GetUnrealizedPl(instrument, trade, float(trade['stopLossOrder']['price']))
        print "STOP LOSS: " + str(trade["unrealizedPL"]) + " pips"
        TotalPips += float(trade["unrealizedPL"])
        print str(TotalPips)
        trades.pop(instrument, None)
        return
    elif trade['type'] == -1 and (float(last_candle['close']) > float(trade['stopLossOrder']['price']) or float(last_candle['high']) > float(trade['stopLossOrder']['price']) or float(last_candle['low']) > float(trade['stopLossOrder']['price'])):
        GetUnrealizedPl(instrument, trade, float(trade['stopLossOrder']['price']))
        print "STOP LOSS: " + str(trade["unrealizedPL"]) + " pips"
        TotalPips += float(trade["unrealizedPL"])
        print str(TotalPips)
        trades.pop(instrument, None)
        return

    GetUnrealizedPl(instrument, trade, float(last_candle['close']))

    if trade.has_key('partially_closed'):
        if CheckTotalClose(instrument, trade['type'], last_candle):
            print instrument + " A CERRAR DEL TODO: " + str(trade["unrealizedPL"]) + " pips"
            TotalPips += float(trade["unrealizedPL"])
            print str(TotalPips)
            trades.pop(instrument, None)
        else:
            CheckTraillingStop(trade, trade['type'], last_candle['close'])
    else:
        if IsFalseSignal(instrument, trade['type']):
            print instrument + " FALSE SIGNAL, A CERRAR DEL TODO: " + str(trade["unrealizedPL"]) + " pips"
            TotalPips += float(trade["unrealizedPL"])
            print str(TotalPips)
            trades.pop(instrument, None)
        else:
            if CheckPartialClose(trade, instrument, trade['type'], last_candle):
                # trade['price'] = float(last_candle['close'])
                trade['stopLossOrder']['price'] = float(trade['price'])
                print instrument + " A CERRAR A MITAD: " + str(trade["unrealizedPL"]) + " pips"
                TotalPips += float(trade["unrealizedPL"])
                print str(TotalPips)
                trade['partially_closed'] = True
                # OrdersData().CloseTradePartially(trade, 0.5);
                # OrdersData().ModifyStopLoss(trade['stopLossOrder']['id'], trade['id'], trade['price']);

def IsFalseSignal(instrument, trade_type):
    global actual_candles_array
    return ichimoku.CheckIsFalseSignal(instrument, trade_type, actual_candles_array)

def CheckTraillingStop(trade, trade_type, actual_price):
    instrument = trade['instrument']
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

    new_stop_loss = apiData.GetPriceFormatted(new_stop_loss,
                                              instrumentsManager.instruments[instrument]['pricePrecision']);

    trade["stopLossOrder"]["price"] = new_stop_loss

    #OrdersData().ModifyStopLoss(trade['stopLossOrder']['id'], trade['id'], str(new_stop_loss));
    print "Upload stop loss from " + instrument + " to " + str(new_stop_loss)


def CheckTotalClose(instrument, trade_type, last_candle):
    if last_candle is None:
        return False;
    else:
        return ichimoku.CheckTotalClose(trade_type, instrument, last_candle)


def CheckPartialClose(trade, instrument, trade_type, last_candle):
    return ichimoku.CheckPartialClose(trade_type, instrument, granularity, float(trade['initialUnits']),
                                      instrumentsManager.instruments[instrument]['pipLocation'],
                                      trade["unrealizedPL"], pip_target)


def GetUnrealizedPl(instrument, trade, actual_price):
    beginning_price = float(trade["price"])

    pip_location = 10 ** instrumentsManager.instruments[instrument]['pipLocation']

    if trade['type'] == 1:
        delta = actual_price - beginning_price
    else:
        delta = beginning_price - actual_price

    #print str(beginning_price) + " - " + str(float(actual_price)) + ": " + str(float(delta / pip_location))

    trade['unrealizedPL'] = float(delta / pip_location)

    return trade['unrealizedPL']


##################################################

if __name__ == "__main__":
    main()
