import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

import pandas as pd
import json
from bs4 import BeautifulSoup
import re

class ApiData(object):

	access_token = ""
	domain = ""
	streaming_domain = ""
	account_id = ""

	def __init__(self, account_id, access_token):
		self.account_id = account_id
		self.access_token = access_token
		self.domain = "api-fxpractice.oanda.com"
		self.streaming_domain = "stream-fxpractice.oanda.com"

	def GetData(self, instrument, granularity, candles_count):
		url = "https://" + self.domain + "/v3/instruments/" + instrument + "/candles"
		headers = { 'Authorization' : 'Bearer ' + self.access_token, 'count': str(candles_count) }
		params = { 'price' : 'M', 'granularity': granularity }

		s = requests.Session()
		req = requests.Request('GET', url, headers = headers, params = params)
		pre = req.prepare()
		response = s.send(pre, stream = False, verify = False)

		if response.status_code != 200:
			return None
		else:
			msg = json.loads(response.text)

			data = []

			if msg.has_key('candles'):
				for candle in msg['candles']:
					data.append({ 'time': candle['time'],
						'open': float(candle['mid']['o']),
						'high': float(candle['mid']['h']),
						'low': float(candle['mid']['l']),
						'close': float(candle['mid']['c']),
						'completed': candle['complete']})

			return pd.DataFrame(data)

	def _connectToStream(self, instrument):
		try:
			s = requests.Session()
			url = "https://" + self.streaming_domain + "/v3/accounts/" + self.account_id +"/pricing/stream"
			headers = { 'Authorization' : 'Bearer ' + self.access_token }
			params = { 'instruments' : instrument }
			req = requests.Request('GET', url, headers = headers, params = params)
			pre = req.prepare()
			resp = s.send(pre, stream = True, verify = False)
			return resp
		except Exception as e:
			s.close()
			print "Caught exception when connecting to stream\n" + str(e)

	def GetStreamingData(self, instruments):
		response = self._connectToStream(instruments)
		if response.status_code != 200:
			return
		for line in response.iter_lines(1):
			msg = json.loads(line)

			if msg.has_key("instrument") or msg.has_key("tick"):
				midPrice = (float(msg['closeoutBid']) + float(msg['closeoutAsk'])) / 2.0
				yield { 'instrument': msg['instrument'], 'price': midPrice }

	def OrderIsStillOpened(self, order_id):

		return None

	def MakeMarketOrder(self, order_id, instrument, datetime, units, stop_loss):
		order = self.GetMarketOrderBody(order_id, instrument, datetime, int(units), stop_loss)

		url = "https://" + self.domain + "/v3/accounts/" + self.account_id + "/orders"
		headers = { 'Authorization' : 'Bearer ' + self.access_token }

		s = requests.Session()
		req = requests.Request('POST', url, headers = headers, json={ "order": order })

		pre = req.prepare()
		response = s.send(pre, stream = False, verify = False)

		msg = json.loads(response.text)

		if msg.has_key('orderFillTransaction'):
			return True
		else:
			return False

	def GetMarketOrderBody(self, order_id, instrument, datetime, units, stop_loss):
		order_type = "MARKET"
		order_time_in_force = "GTC"
		order_position_fill = "DEFAULT"

		client_extension = {}
		client_extension['id'] = order_id
		client_extension['tag'] = instrument + "_" + str(datetime)
		client_extension['comment'] = instrument + "_" + str(datetime)

		stop_loss_details = {}
		stop_loss_details['price'] = stop_loss
		stop_loss_details['clientExtension'] = client_extension

		return_json = {}
		return_json['type'] = order_type
		return_json['instrument'] = instrument
		return_json['units'] = units
		return_json['clientExtensions'] = client_extension
		return_json['stopLossOnFill'] = stop_loss_details

		return return_json

	def GetUnitsForPrice(self, price, instrument, rate = 1):
		local_currency = "EUR";
		base_currency = instrument.split('_')[0];

		if base_currency == local_currency:
			last_close_price = 1;
		else:
			currency_to_check = base_currency + "_" + local_currency;
			last_close_price = self.GetConvertPriceCurrencyWithGoogle(local_currency, base_currency)

		return float(price) * rate / float(last_close_price);

	def GetAllInstrumentsTradeable(self):

		url = "https://" + self.domain + "/v3/accounts/" + self.account_id + "/instruments"
		headers = { 'Authorization' : 'Bearer ' + self.access_token }

		s = requests.Session()
		req = requests.Request('GET', url, headers = headers)

		pre = req.prepare()
		response = s.send(pre, stream = False, verify = False)

		msg = json.loads(response.text)
		return msg

	def GetActualPrice(self, instrument):
		data = self.GetData(instrument, "M5", 10)
		if data is None:
			return None;
		return float(data[-1:]['close'])

	def GetLastCandle(self, instrument, granularity):
		data = self.GetData(instrument, granularity, 10)
		if data is None:
			return None;
		return data[-1:];

	def GetTradesOpened(self):
		url = "https://" + self.domain + "/v3/accounts/" + self.account_id + "/openTrades"
		headers = { 'Authorization' : 'Bearer ' + self.access_token }
		#params = { 'price' : 'M', 'granularity': granularity }

		s = requests.Session()
		req = requests.Request('GET', url, headers = headers)
		pre = req.prepare()
		response = s.send(pre, stream = False, verify = False)
		msg = json.loads(response.text);

		if msg.has_key("trades") and len(msg['trades']) > 0:
			return msg['trades'];
		else:
			return [];

	def CloseTradePartially(self, trade, percent):
		units_to_close = int(float(trade['currentUnits']) * percent);
		if units_to_close < 0:
			units_to_close = units_to_close * -1;

		if units_to_close == 0:
			units_to_close = "ALL";

		url = "https://" + self.domain + "/v3/accounts/" + self.account_id + "/trades/" + trade['id'] + "/close";
		headers = { 'Authorization' : 'Bearer ' + self.access_token }

		s = requests.Session()
		req = requests.Request('PUT', url, headers = headers, json={ "units": str(units_to_close) })
		pre = req.prepare()
		response = s.send(pre, stream = False, verify = False)
		msg = json.loads(response.text);

		if response.status_code != 200:
			print str(units_to_close);
			print msg;

		return response.status_code == 200;

	def GetCurrencyChange(self, instrument):
		local_currency = "EUR";
		base_currency = instrument.split('_')[1];

		if base_currency == local_currency:
			last_close_price = 1;
		else:
			currency_to_check = base_currency + "_" + local_currency;
			last_close_price = self.GetConvertPriceCurrencyWithGoogle(local_currency, base_currency)

		return last_close_price;

	def GetConvertPriceCurrencyWithGoogle(self, currency_A, currency_B):
		url = "https://www.google.com/finance/converter?a=1&from=" + currency_A + "&to=" + currency_B
		s = requests.Session()
		req = requests.Request('GET', url)
		pre = req.prepare()
		response = s.send(pre, stream = False, verify = False)
		soup = BeautifulSoup(response.text, 'html.parser')
		span = soup.find("span", attrs = {"class":"bld"});
		data = span.get_text()
		r = re.compile("[0-9\.]")
		price = "";
		for v in r.findall(data):
			price += v;

		return float(price);

	def GetPipValue(self, instrument, units):
		if units < 0:
			units = units * -1;

		currency_change_price = self.GetCurrencyChange(instrument);

		if currency_change_price == 0:
			return 0;
		else:
			return (0.0001 * units) / currency_change_price;

	def ModifyStopLoss(self, trade_id, stop_loss_id, new_stop_loss):
		url = "https://" + self.domain + "/v3/accounts/" + self.account_id + "/orders/" + trade_id;
		headers = { 'Authorization' : 'Bearer ' + self.access_token }

		s = requests.Session()
		req = requests.Request('PUT', url, headers = headers, json={'order': self._getStopLossOrderBody(stop_loss_id, new_stop_loss)});
		pre = req.prepare()
		response = s.send(pre, stream = False, verify = False)
		msg = json.loads(response.text);

		if response.status_code != 200:
			print msg;

		return msg;
	def _getStopLossOrderBody(self, trade_id, new_stop_loss):
		order_type = "STOP_LOSS"
		order_time_in_force = "GTC"
		trade_id = trade_id;
		new_price = new_stop_loss;

		return_json = {};
		return_json['type'] = order_type;
		return_json['tradeID'] = trade_id;
		return_json['price'] = new_price;
		return_json['timeInForce'] = order_time_in_force;

		return return_json;

	def GetLastClosedCandle(self, instrument, granularity):
		data = self.GetData(instrument, granularity, 10)
		if data is None:
			return None;

		index = -1;
		last_candle = data[index:].iloc[0];

		while(last_candle['completed'] == False):
			index = index - 1;
			last_candle = data[index:].iloc[0];

		return last_candle;

	def ExistsTradeOfInstrument(self, instrument):
		url = "https://" + self.domain + "/v3/accounts/" + self.account_id + "/openTrades"
		headers = { 'Authorization' : 'Bearer ' + self.access_token }

		s = requests.Session()
		req = requests.Request('GET', url, headers = headers)
		pre = req.prepare()
		response = s.send(pre, stream = False, verify = False)
		msg = json.loads(response.text);

		if msg.has_key("trades") and len(msg['trades']) > 0:
			for trade in msg['trades']:
				if trade['instrument'] == instrument:
					return True;

		return False;

	def GetClosedTrades(self):
		url = "https://" + self.domain + "/v3/accounts/" + self.account_id + "/trades"
		headers = { 'Authorization' : 'Bearer ' + self.access_token }
		params = {'state': 'CLOSED'}
		s = requests.Session()
		req = requests.Request('GET', url, headers = headers, params = params)
		pre = req.prepare()
		response = s.send(pre, stream = False, verify = False)
		msg = json.loads(response.text);

		for trade in msg['trades']:
			print trade;
			print "----";
