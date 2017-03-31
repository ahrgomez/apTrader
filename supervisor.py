from lib import ApiData
from strategies import Ichimoku
from time import sleep

access_token = '362c69e15045ab046662317d02837de5-abe03f3f1c7b18419930866fe2bd69b0'
account_id = '101-004-5177797-001'

apiData = ApiData.ApiData(account_id, access_token)
ichimoku = Ichimoku.Ichimoku(account_id, access_token)

def main():
    while(True):
        try:
            print "Init supervisor"
            print "----------------"
            InitProcess();
            print "----------------"
        except KeyboardInterrupt:
			break;
        except e:
            print e
            pass;

def InitProcess():
    trades = apiData.GetTradesOpened()
    for trade in trades:

        instrument = trade['instrument'];

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
        if CheckTotalClose(trade, trade_type):
            print instrument + " A CERRAR DEL TODO";
            apiData.CloseTradePartially(trade, 0);
        else:
            actual_price = float(apiData.GetActualPrice(trade['instrument']));
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

            new_stop_loss = float('{0:.6g}'.format(new_stop_loss))
            print new_stop_loss
            apiData.ModifyStopLoss(trade['stopLossOrder']['id'], trade['id'], str(new_stop_loss));
            print "Upload stop loss from " + instrument + " to " + str(new_stop_loss);
    else:
        if CheckPartialClose(trade, trade_type):
            print instrument + " A CERRAR A MITAD";
            apiData.CloseTradePartially(trade, 0.5);
            apiData.ModifyStopLoss(trade['stopLossOrder']['id'], trade['id'], trade['price']);


def CheckTotalClose(trade, trade_type):
    last_candle = apiData.GetLastClosedCandle(trade['instrument'], "H1");
    if last_candle is None:
        return False;
    else:
        return ichimoku.CheckTotalClose(trade_type, trade['instrument'], last_candle);

def CheckPartialClose(trade, trade_type):
    return ichimoku.CheckPartialClose(trade_type, trade['instrument'], float(trade['initialUnits']), float(trade['unrealizedPL']));

if __name__ == "__main__":
    main()
