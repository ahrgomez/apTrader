import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

import pandas as pd
import json

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
						'high': float(candle['mid']['h']),
						'low': float(candle['mid']['l']),
						'close': float(candle['mid']['c'])})

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
		client_extension['id'] = "d5f687eb-f220-11e6-88e4-6c4008b00e3c"
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

	def GetUnitsForPrice(self, price, instrument, last_close_price, rate = 1):
		local_currency = "EUR";
		base_currency = instrument.split('_')[0];

		if base_currency == local_currency:
			return price;

		currency_to_check = base_currency + "_" + local_currency;

		data = self.GetData(currency_to_check, "H1", 10);

		if data is None:
			currency_to_check = local_currency + "_" + base_currency;
			data = self.GetData(currency_to_check, "H1", 10);

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
		return float(data[-1:]['close'])

	def GetTradesOpened(self):
		url = "https://" + self.domain + "/v3/accounts/"
		headers = { 'Authorization' : 'Bearer ' + self.access_token }
		#params = { 'price' : 'M', 'granularity': granularity }

		s = requests.Session()
		req = requests.Request('GET', url, headers = headers)
		pre = req.prepare()
		response = s.send(pre, stream = False, verify = False)
		print url
		print response.text
