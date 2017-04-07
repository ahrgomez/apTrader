import settings
import requests
import json

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

from datetime import datetime, timedelta

class OrdersData(object):

    def MakeMarketOrder(self, order_id, instrument, datetime, units, stop_loss):
    	order = self._getMarketOrderBody(order_id, instrument, datetime, units, stop_loss)

    	url = "https://" + settings.API_DOMAIN + "/v3/accounts/" + settings.ACCOUNT_ID + "/orders"
    	headers = { 'Authorization' : 'Bearer ' + settings.ACCESS_TOKEN }

    	s = requests.Session()
    	req = requests.Request('POST', url, headers = headers, json={ "order": order })

    	pre = req.prepare()
    	response = s.send(pre, stream = False, verify = False)

    	if response.status_code != 201:
    		raise Exception('api.OrdersData.MakeMarketOrder: Instrument: ' + instrument + ' units: ' + str(units) + ' stop_loss: ' + str(stop_loss) + ' Response: ' + response.text)

    	msg = json.loads(response.text)

    	if msg.has_key('orderFillTransaction'):
    		return True
    	else:
    		return False

    def _getMarketOrderBody(self, order_id, instrument, datetime, units, stop_loss):
    	order_type = "MARKET"
    	order_time_in_force = "GTC"
    	order_position_fill = "DEFAULT"

    	client_extension = {}
    	client_extension['id'] = order_id
    	client_extension['tag'] = instrument + "_" + str(datetime)
    	client_extension['comment'] = instrument + "_" + str(datetime)

    	stop_loss_details = {}
    	stop_loss_details['price'] = str(stop_loss);
    	stop_loss_details['clientExtension'] = client_extension

    	return_json = {}
    	return_json['type'] = order_type
    	return_json['instrument'] = instrument
    	return_json['units'] = str(units);
    	return_json['clientExtensions'] = client_extension
    	return_json['stopLossOnFill'] = stop_loss_details

    	return return_json

    def MakeLimitOrder(self, order_id, instrument, price, datetime, units, stop_loss):
    	order = self._getLimitOrderBody(order_id, instrument, price, datetime, units, stop_loss)

    	url = "https://" + settings.API_DOMAIN + "/v3/accounts/" + settings.ACCOUNT_ID + "/orders"
    	headers = { 'Authorization' : 'Bearer ' + settings.ACCESS_TOKEN }

    	s = requests.Session()
    	req = requests.Request('POST', url, headers = headers, json={ "order": order })

    	pre = req.prepare()
    	response = s.send(pre, stream = False, verify = False)

    	if response.status_code != 201:
    		raise Exception('api.OrdersData.MakeMarketOrder: Instrument: ' + instrument + ' units: ' + str(units) + ' stop_loss: ' + str(stop_loss) + ' Response: ' + response.text)

    	msg = json.loads(response.text)

    	if msg.has_key('orderFillTransaction'):
    		return True
    	else:
    		return False

    def _getLimitOrderBody(self, order_id, instrument, price, datetime, units, stop_loss):
    	order_type = "MARKET_IF_TOUCHED";
    	order_time_in_force = "GTD";
    	order_position_fill = "DEFAULT";
        time_to_cancel = datetime.now() + timedelta(hours=1);
        time_to_cancel = str(time_to_cancel.isoformat('T')) + "Z";

    	client_extension = {};
    	client_extension['id'] = order_id;
    	client_extension['tag'] = instrument + "_" + str(datetime);
    	client_extension['comment'] = instrument + "_" + str(datetime);

    	stop_loss_details = {};
    	stop_loss_details['price'] = str(stop_loss);
    	stop_loss_details['clientExtension'] = client_extension;

    	return_json = {};
    	return_json['type'] = order_type;
    	return_json['instrument'] = instrument;
        return_json['timeInForce'] = order_time_in_force;
        return_json['gtdTime'] = time_to_cancel;
    	return_json['units'] = str(units);
        return_json['price'] = str(price);
    	return_json['clientExtensions'] = client_extension;
    	return_json['stopLossOnFill'] = stop_loss_details;

    	return return_json;

    def ModifyStopLoss(self, trade_id, stop_loss_id, new_stop_loss):
    	url = "https://" + settings.API_DOMAIN + "/v3/accounts/" + settings.ACCOUNT_ID + "/orders/" + trade_id;
    	headers = { 'Authorization' : 'Bearer ' + settings.ACCESS_TOKEN }

    	s = requests.Session()
    	req = requests.Request('PUT', url, headers = headers, json={'order': self._getStopLossOrderBody(stop_loss_id, str(new_stop_loss))});
    	pre = req.prepare()
    	response = s.send(pre, stream = False, verify = False)
    	msg = json.loads(response.text);

    	if response.status_code != 201:
    		raise Exception('api.OrdersData.ModifyStopLoss: ' + response.text)

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

    def CloseTradePartially(self, trade, percent):
		units_to_close = int(float(trade['currentUnits']) * percent);
		if units_to_close < 0:
			units_to_close = units_to_close * -1;

		if units_to_close == 0:
			units_to_close = "ALL";

		url = "https://" + settings.API_DOMAIN + "/v3/accounts/" + settings.ACCOUNT_ID + "/trades/" + trade['id'] + "/close";
		headers = { 'Authorization' : 'Bearer ' + settings.ACCESS_TOKEN }

		s = requests.Session()
		req = requests.Request('PUT', url, headers = headers, json={ "units": str(units_to_close) })
		pre = req.prepare()
		response = s.send(pre, stream = False, verify = False)

		if response.status_code != 200:
			raise Exception('api.OrdersData.CloseTradePartially: Instrument: ' + trade['instrument'] + ' Percent: ' + str(percent) + ' Response: ' + response.text)

		msg = json.loads(response.text);

		if response.status_code != 200:
			print str(units_to_close);
			print msg;

		return response.status_code == 200;
