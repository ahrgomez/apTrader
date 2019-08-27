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

import sys, os

apiData = ApiData()
instrumentsManager = InstrumentsManager({})
errorsManagement = Client('https://7932a7da676c4962895957059416bd7d:da9a1669ee724bb2b61cf7b47b430ccc@sentry.io/154029')

# Strategies
granularity = "M30"
ichimoku = Ichimoku.Ichimoku(granularity)

DEBUG = True;


def main():
    instruments_list = "";
    instruments = GetTradeableInstrumentsByRanking()
    for inst in instruments:
        print inst
        instruments_list += inst + ",";

    while (True):
        try:
            if IsForbiddenTime():
                print "BOLSA CERRADA";
                sleep(60);
                continue;

            pricesStream = PricesStream();

            for tick in pricesStream.GetStreamingData(instruments_list):
                if IsForbiddenTime():
                    print "BOLSA CERRADA";
                    sleep(60);
                    break;

                instrument = tick['instrument']
                price = tick['price']

                instrument_part_A = instrument.split('_')[0];
                instrument_part_A = instrument_part_A.encode('ascii', 'ignore');
                instrument_part_B = instrument.split('_')[1];
                instrument_part_B = instrument_part_B.encode('ascii', 'ignore');

                instrument = instrument_part_A + '_' + instrument_part_B;

                if instrument == "EU50_EUR" or instrument == "DE30_EUR" or instrument == "FR40_EUR" or instrument == "NL25_EUR" or instrument == "XAU_EUR":
                    continue

                result = ProcessPrice(instrument, price);
                if DEBUG:
                    if result == 1:
                        print instrument + ": " + "LONG"
                    elif result == -1:
                        print instrument + ": " + "SHORT"
        except KeyboardInterrupt:
            break;
        except Exception, e:
            print "error!"
            traceback.print_exc()

            errorsManagement.captureException();
            pass;


def ProcessPrice(instrument, price):
    check_result, entry_price, stop_loss_price, time = ichimoku.Verify(instrument)
    if check_result is None:
        return

    # if apiData.GetMarginUsed() >= 400:
    #	return

    if PutOrder(check_result, instrument, entry_price, price, stop_loss_price):
        print time + ": " + str(entry_price) + "/" + str(stop_loss_price)
        return check_result;
    else:
        return None;


def PutOrder(order_type, instrument, entry_price, price, stop_loss):
    if apiData.ExistsOrderOfInstrument(instrument):
        could_put_order = False
    else:
        if apiData.ExistsTradeOfInstrument(instrument):
            trades = apiData.GetTradesOpened()
            instrument_trades = []

            complete_trade_found = False

            for trade in trades:
                if trade['instrument'] == instrument:
                    instrument_trades.append(trade)
                    partial = False
                    if float(trade['initialUnits']) < 0:
                        partial = float(trade['initialUnits']) < float(trade['currentUnits'])
                    else:
                        partial = float(trade['initialUnits']) > float(trade['currentUnits'])

                    if not partial:
                        complete_trade_found = True

            if len(instrument_trades) == 0 and apiData.ExistsOrderOfInstrument(instrument):
                could_put_order = False
            else:
                sorted(instrument_trades,
                       key=lambda x: datetime.strptime(x['openTime'].split('.')[0], '%Y-%m-%dT%H:%M:%S'))

                last_trade = instrument_trades[0]

                partially_closed = False
                if float(last_trade['initialUnits']) < 0:
                    partially_closed = float(last_trade['initialUnits']) < float(last_trade['currentUnits'])
                else:
                    partially_closed = float(last_trade['initialUnits']) > float(last_trade['currentUnits'])

                if partially_closed and not complete_trade_found:
                    print instrument + ": A GANADORA"
                    could_put_order = True
                else:
                    could_put_order = False
        else:
            could_put_order = True

    if could_put_order:
        date = datetime.now()

        balance = apiData.GetBalance()

        units = apiData.GetUnitsForPrice(balance * 0.01, instrument,
                                     instrumentsManager.instruments[instrument]['precision'], granularity,
                                     instrumentsManager.instruments[instrument]['rate'])

        if units is None or units == 0:
            print "Can't have units to " + instrument
            return None

        order_id = str(uuid.uuid1())

        stop_loss = apiData.GetPriceFormatted(stop_loss, instrumentsManager.instruments[instrument]['pricePrecision'])

        total_units = order_type * float(units)

        entry_price = apiData.GetPriceFormatted(entry_price,
                                                instrumentsManager.instruments[instrument]['pricePrecision'])

        result = False

        try:
            result = OrdersData().MakeMarketOrder(order_id, instrument, date, total_units, stop_loss)
            #if order_type == 1:
                #if entry_price < price:
                #    result = OrdersData().MakeMarketOrder(order_id, instrument, date, total_units, stop_loss)
                #else:
                #    result = OrdersData().MakeLimitOrder(order_id, instrument, entry_price, date, total_units, stop_loss)
            #else:
                #if entry_price > price:
                #    result = OrdersData().MakeMarketOrder(order_id, instrument, date, total_units, stop_loss)
                #else:
                #    result = OrdersData().MakeLimitOrder(order_id, instrument, entry_price, date, total_units, stop_loss)
        except Exception:
            traceback.print_exc()
            errorsManagement.captureException()
            pass

        if result:
            print "Made " + instrument + " order with id " + order_id + " with " + str(order_type * units) + " units"
            return True

    return False


def GetTradeableInstrumentsByRanking():
    instrumentsManager.GetTradeableInstruments()
    balance = apiData.GetBalance()

    instruments = []

    for instrument in instrumentsManager.instruments:
        try:
            if instrument == "EU50_EUR" or instrument == "DE30_EUR" or instrument == "FR40_EUR" or instrument == "NL25_EUR" or instrument == "XAU_EUR":
                continue

            pip_value = apiData.GetPipValue(instrument, balance * 0.01,
                                            instrumentsManager.instruments[instrument]['pipLocation'], granularity)
            if pip_value > 0.02:
                instruments.append(instrument)
        except:
            pass

    return instruments


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
