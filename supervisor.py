from lib import ApiData
from strategies import Ichimoku
from time import sleep

access_token = '362c69e15045ab046662317d02837de5-abe03f3f1c7b18419930866fe2bd69b0'
account_id = '101-004-5177797-001'

apiData = ApiData.ApiData(account_id, access_token)
ichimoku = Ichimoku.Ichimoku(account_id, access_token)

def main():
    while(True):
        print "Init supervisor"
        print "----------------"
        InitProcess();
        print "----------------"
        print "Waiting 15 seconds..."
        sleep(15);

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

            if begining_price == stop_loss_price:
                if trade_type == 1:
                    bigger_item = actual_price;
                    lower_item = stop_loss_price;
                else:
                    bigger_item = stop_loss_price;
                    lower_item = actual_price;

                bi_decimals = bigger_item - int(bigger_item);
                li_decimals = lower_item - int(lower_item);

                if bi_decimals / li_decimals >= 1:
                    new_stop_loss = lower_item + ((bi_decimals - li_decimals) / 2);
                    apiData.ModifyStopLoss(trade['stopLossOrder']['id'], trade['id'], new_stop_loss);
                    print "Upload stop loss from " + instrument + " to " + str(new_stop_loss);
    else:
        if CheckPartialClose(trade, trade_type):
            print instrument + " A CERRAR A MITAD";
            apiData.CloseTradePartially(trade, 0.5);
            apiData.ModifyStopLoss(trade['stopLossOrder']['id'], trade['id'], trade['price']);


def CheckTotalClose(trade, trade_type):
    last_candle = apiData.GetLastCandle(trade['instrument'], "H1");
    if last_candle is None:
        return False;
    else:
        return ichimoku.CheckTotalClose(trade_type, trade['instrument'], last_candle);

def CheckPartialClose(trade, trade_type):
    return ichimoku.CheckPartialClose(trade_type, trade['instrument'], float(trade['initialUnits']), float(trade['unrealizedPL']));

if __name__ == "__main__":
    main()
