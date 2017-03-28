from lib import ApiData
from strategies import Ichimoku

access_token = '362c69e15045ab046662317d02837de5-abe03f3f1c7b18419930866fe2bd69b0'
account_id = '101-004-5177797-001'

apiData = ApiData.ApiData(account_id, access_token)

def main():
    trades = apiData.GetTradesOpened()
    for trade in trades:
        print trade;
        intrument = trade['instrument'];
        trade_type = float(trade['initialUnits']) / (float(trade['initialUnits']) * -1);
        apiData.CloseTradePartially(trade, 0.5);

if __name__ == "__main__":
    main()
