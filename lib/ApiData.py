import settings

import requests

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

import pandas as pd
import json
from bs4 import BeautifulSoup
import re

import math

class ApiData(object):

	def GetData(self, instrument, granularity, candles_count):
		url = "https://" + settings.API_DOMAIN + "/v3/instruments/" + instrument + "/candles"
		headers = { 'Authorization' : 'Bearer ' + settings.ACCESS_TOKEN, 'count': str(candles_count) }
		params = { 'price' : 'M', 'granularity': granularity }

		s = requests.Session()
		req = requests.Request('GET', url, headers = headers, params = params)
		pre = req.prepare()
		response = s.send(pre, stream = False, verify = False)

		if response.status_code != 200:
			raise Exception('GetData: Instrument:' + instrument + ' Response:' + response.text)
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

	def GetUnitsForPrice(self, price, instrument, precision, rate = 1):
		local_currency = "EUR";
		base_currency = instrument.split('_')[0];

		if base_currency == local_currency:
			last_close_price = 1;
		else:
			currency_to_check = base_currency + "_" + local_currency;
			last_close_price = self.GetConvertPriceCurrencyWithOanda(local_currency, base_currency)

		units =  float(price) * rate / float(last_close_price);
		units = self.GetPriceFormatted(units, int(precision));

		return units;

	def GetPriceFormatted(self, f, n):
		is_negative = False;
		if f < 0:
			is_negative = True;
			f = f * -1;
		s = '%.12f'%f;
		i, p, d = s.partition('.');

		if n == 0:
			if is_negative:
				i = i * -1;
			return int(i);
		else:
			if n > 0:
				new_value = '.'.join([i, (d+'0'*n)[:n]]);
			else:
				new_value = i;

			if is_negative:
				new_value = float(new_value * -1);

			return new_value;

	def GetAllInstrumentsTradeable(self):

		url = "https://" + settings.API_DOMAIN + "/v3/accounts/" + settings.ACCOUNT_ID + "/instruments"
		headers = { 'Authorization' : 'Bearer ' + settings.ACCESS_TOKEN }

		s = requests.Session()
		req = requests.Request('GET', url, headers = headers)

		pre = req.prepare()
		response = s.send(pre, stream = False, verify = False)

		if response.status_code != 200:
			raise Exception('GetAllInstrumentsTradeable: ' + response.text)

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
		url = "https://" + settings.API_DOMAIN + "/v3/accounts/" + settings.ACCOUNT_ID + "/openTrades"
		headers = { 'Authorization' : 'Bearer ' + settings.ACCESS_TOKEN }
		#params = { 'price' : 'M', 'granularity': granularity }

		s = requests.Session()
		req = requests.Request('GET', url, headers = headers)
		pre = req.prepare()
		response = s.send(pre, stream = False, verify = False)

		if response.status_code != 200:
			raise Exception('GetTradesOpened: ' + response.text)

		msg = json.loads(response.text);

		if msg.has_key("trades") and len(msg['trades']) > 0:
			return msg['trades'];
		else:
			return [];

	def GetCurrencyChange(self, instrument):
		local_currency = "EUR";
		base_currency = instrument.split('_')[1];

		if base_currency == local_currency:
			last_close_price = 1;
		else:
			currency_to_check = base_currency + "_" + local_currency;
			last_close_price = self.GetConvertPriceCurrencyWithOanda(local_currency, base_currency)

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

	def GetConvertPriceCurrencyWithFixer(self, currency_A, currency_B):
		status = 504;

		while(status == 504 or status == 502):
			url = "http://api.fixer.io/latest?base=" + currency_A;
			s = requests.Session()
			req = requests.Request('GET', url);
			pre = req.prepare()
			response = s.send(pre, stream = False, verify = False)
			status = response.status_code;

		msg = json.loads(response.text);
		return msg['rates'][currency_B];

	def GetConvertPriceCurrencyWithOanda(self, currency_A, currency_B):
		to_check = currency_A + "_" + currency_B;
		actual_price = self.GetActualPrice(to_check);
		return actual_price;

	def GetPipValue(self, instrument, units, pip_location):
		if units < 0:
			units = units * -1;

		currency_change_price = self.GetCurrencyChange(instrument);

		if currency_change_price == 0:
			return 0;
		else:
			pip_location = pip_location * -1;
			div = 1;
			while(pip_location > 0):
				div = div * 10;
				pip_location = pip_location - 1;

			pip_location = 1.0 / div;
			return (pip_location * units) / currency_change_price;

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
		url = "https://" + settings.API_DOMAIN + "/v3/accounts/" + settings.ACCOUNT_ID + "/openTrades"
		headers = { 'Authorization' : 'Bearer ' + settings.ACCESS_TOKEN }

		s = requests.Session()
		req = requests.Request('GET', url, headers = headers)
		pre = req.prepare()
		response = s.send(pre, stream = False, verify = False)

		if response.status_code != 200:
			raise Exception('ExistsTradeOfInstrument: ' + response.text)

		msg = json.loads(response.text);

		if msg.has_key("trades") and len(msg['trades']) > 0:
			for trade in msg['trades']:
				if trade['instrument'] == instrument:
					return True;

		return False;

	def GetClosedTrades(self):
		url = "https://" + settings.API_DOMAIN + "/v3/accounts/" + settings.ACCOUNT_ID + "/trades"
		headers = { 'Authorization' : 'Bearer ' + settings.ACCESS_TOKEN }
		params = {'state': 'CLOSED'}
		s = requests.Session()
		req = requests.Request('GET', url, headers = headers, params = params)
		pre = req.prepare()
		response = s.send(pre, stream = False, verify = False)

		if response.status_code != 200:
			raise Exception('GetClosedTrades: ' + response.text)

		msg = json.loads(response.text);

		return msg['trades'];
