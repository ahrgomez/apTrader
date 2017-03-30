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
        print "Waiting 60 seconds..."
        sleep(60);

def InitProcess():
    trades = apiData.GetTradesOpened()
    for trade in trades:

        instrument = trade['instrument'];
        trade_type = float(trade['initialUnits']) / (float(trade['initialUnits']) * -1);
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
        if CheckPartialClose(trade, trade_type):
            print instrument + " A CERRAR A MITAD";
            apiData.CloseTradePartially(trade, 0.5);


def CheckTotalClose(trade, trade_type):
    last_candle = apiData.GetLastCandle(trade['instrument'], "H1");
    if last_candle is None:
        return False;
    else:
        return ichimoku.CheckTotalClose(trade_type, trade['instrument'], last_candle);

def CheckPartialClose(trade, trade_type):
    pip_value = apiData.GetPipValue(trade['instrument'], float(trade['initialUnits']));
    print trade['instrument']
    print pip_value
    print trade
    print "-------------"
    if trade_type == 1:
        if (float(trade['unrealizedPL']) / pip_value) > 60:
            return False;
    else:
        if (float(trade['unrealizedPL']) / pip_value) < -60:
            return False;
    return False;

if __name__ == "__main__":
    main()
