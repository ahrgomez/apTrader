from lib.ApiData import ApiData
from lib.InstrumentsManager import InstrumentsManager

from api.OrdersData import OrdersData

from strategies.Ichimoku import Ichimoku
from time import sleep
from raven import Client
from datetime import datetime

errorsManagement = Client('https://7aff590e4b774a43ba2255f9e1dcbeff:e88ee295381e4c24bb700e71024e8ba2@sentry.io/154033')

apiData = ApiData()
instrumentsManager = InstrumentsManager({})
ichimoku = Ichimoku()

DEBUG = False;

def main():
    instrumentsManager.GetTradeableInstruments();

    while(True):
        try:
            if IsForbiddenTime():
				print "BOLSA CERRADA";
				sleep(60);
				continue;

            if DEBUG:
                print "----------------"
                print "Init supervisor"
                print "----------------"

            InitProcess();
        except KeyboardInterrupt:
			break;
        except:
            errorsManagement.captureException();
            pass;

def InitProcess():
    trades = apiData.GetTradesOpened()
    for trade in trades:

        instrument = trade['instrument'];

        instrument_part_A = instrument.split('_')[0];
        instrument_part_A = instrument_part_A.encode('ascii','ignore');
        instrument_part_B = instrument.split('_')[1];
        instrument_part_B = instrument_part_B.encode('ascii','ignore');

        instrument = instrument_part_A + '_' + instrument_part_B;

        if float(trade['initialUnits']) < 0:
            trade_type = -1;
        else:
            trade_type = 1;

        partially_closed = False;

        if float(trade['initialUnits']) < 0:
            partially_closed = float(trade['initialUnits']) < float(trade['currentUnits']);
        else:
            partially_closed = float(trade['initialUnits']) > float(trade['currentUnits']);

        CheckToCloseTrade(trade, instrument, trade_type, partially_closed);

def CheckToCloseTrade(trade, instrument, trade_type, partially_closed):

    if partially_closed:
        if CheckTotalClose(instrument, trade_type):
            print instrument + " A CERRAR DEL TODO";
            OrdersData().CloseTradePartially(trade, 0);
        else:
            actual_price = float(apiData.GetActualPrice(instrument));
            stop_loss_price = float(trade['stopLossOrder']['price']);
            begining_price = float(trade['price']);

            if trade_type == 1:
                if begining_price > stop_loss_price:
                    return;
                else:
                    last_candle = apiData.GetLastClosedCandle(instrument, "H1")
                    if stop_loss_price >= last_candle['low']:
                        return;
                    else:
                        new_stop_loss = last_candle['low'];
            elif trade_type == -1:
                if begining_price < stop_loss_price:
                    return;
                else:
                    last_candle = apiData.GetLastClosedCandle(instrument, "H1")
                    if stop_loss_price <= last_candle['high']:
                        return;
                    else:
                        new_stop_loss = last_candle['high'];

            new_stop_loss = apiData.GetPriceFormatted(new_stop_loss, instrumentsManager.instruments['pricePrecision']);

            OrdersData().ModifyStopLoss(trade['stopLossOrder']['id'], trade['id'], str(new_stop_loss));
            print "Upload stop loss from " + instrument + " to " + str(new_stop_loss);
    else:
        if CheckPartialClose(trade, instrument, trade_type):
            print instrument + " A CERRAR A MITAD";
            OrdersData().CloseTradePartially(trade, 0.5);
            OrdersData().ModifyStopLoss(trade['stopLossOrder']['id'], trade['id'], trade['price']);


def CheckTotalClose(instrument, trade_type):
    last_candle = apiData.GetLastClosedCandle(instrument, "H1");
    if last_candle is None:
        return False;
    else:
        return ichimoku.CheckTotalClose(trade_type, instrument, last_candle);

def CheckPartialClose(trade, instrument, trade_type):
    return ichimoku.CheckPartialClose(trade_type, instrument, float(trade['initialUnits']), instrumentsManager.instruments[instrument]['pipLocation'], float(trade['unrealizedPL']));

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
