import settings
import requests
import json

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class PricesStream(object):

	def GetStreamingData(self, instruments):
		response = self._connectToStream(instruments)
		if response.status_code != 200:
			raise Exception('api.PricesStream.GetStreamingData: ' + response.text)
		for line in response.iter_lines(1):
			msg = json.loads(line)

			if msg.has_key("instrument") or msg.has_key("tick"):
				midPrice = (float(msg['closeoutBid']) + float(msg['closeoutAsk'])) / 2.0
				yield { 'instrument': msg['instrument'], 'price': midPrice }

	def _connectToStream(self, instrument):
		try:
			s = requests.Session()
			url = "https://" + settings.STREAM_DOMAIN + "/v3/accounts/" + settings.ACCOUNT_ID +"/pricing/stream"
			headers = { 'Authorization' : 'Bearer ' + settings.ACCESS_TOKEN }
			params = { 'instruments' : instrument }
			req = requests.Request('GET', url, headers = headers, params = params)
			pre = req.prepare()
			resp = s.send(pre, stream = True, verify = False)
			return resp
		except Exception as e:
			s.close()
			print "Caught exception when connecting to stream\n" + str(e)
