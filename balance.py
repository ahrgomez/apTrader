
from lib import ApiData
from dateutil import parser
from datetime import datetime

access_token = '362c69e15045ab046662317d02837de5-abe03f3f1c7b18419930866fe2bd69b0'
account_id = '101-004-5177797-001'

apiData = ApiData.ApiData(account_id, access_token)

def main():
	negative = 0.0;
	positive = 0.0;
	for trade in apiData.GetClosedTrades():
		datetime_object = parser.parse(trade['closeTime']);

		if datetime_object.date() < datetime.today().date():
			continue;

		value = float(trade['realizedPL']);
		financing = float(trade['financing']);
		
		value = value + financing;

		if(value < 0):
			negative = negative - value;
		else:
			positive = positive + value;

	print "Negative: " + str(negative);
	print "----"
	print "Positive: " + str(positive);
	print "----"
	print "Total: " + str(positive - negative);

if __name__ == "__main__":
    main()
