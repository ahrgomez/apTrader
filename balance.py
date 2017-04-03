
from lib.ApiData import ApiData
from dateutil import parser
from datetime import datetime

access_token = '362c69e15045ab046662317d02837de5-abe03f3f1c7b18419930866fe2bd69b0'
account_id = '101-004-5177797-001'

apiData = ApiData()

def main():
	negative = 0.0;
	positive = 0.0;

	realizedPLPositive = 0.0;
	realizedPLNegative = 0.0;

	for trade in apiData.GetTradesOpened():
		rpl = trade['realizedPL'];
		rpl = float(rpl);
		if rpl < 0:
			rpl = rpl * -1;
			realizedPLNegative = realizedPLNegative - rpl;
		else:
			realizedPLPositive = realizedPLPositive + rpl;

	for trade in apiData.GetClosedTrades():
		datetime_object = parser.parse(trade['closeTime']);

		if datetime_object.date() < datetime.today().date():
			continue;

		value = float(trade['realizedPL']);
		financing = float(trade['financing']);

		value = value + financing;

		if(value < 0):
			value = value * -1;
			negative = negative - value;
		else:
			positive = positive + value;

	print "Negative today: " + str(negative + realizedPLNegative);
	print "----"
	print "Positive today: " + str(positive + realizedPLPositive);
	print "----"
	print "Total: " + str((positive + realizedPLPositive) + (negative + realizedPLNegative));

if __name__ == "__main__":
    main()
