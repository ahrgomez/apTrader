from lib import ApiData

class InstrumentsManager(object):

    instruments = {}
    apiData = {}

    def __init__(self, instruments = {}, api_account_id = "", api_access_token = ""):
        self.instruments = instruments
        self.apiData = ApiData.ApiData(api_account_id, api_access_token)
        self.GetTradeableInstruments()

    def Add(self, instrument, data):
    	self.instruments[instrument] = data;

    def ExistsInstrument(self, instrument):
        return self.instruments.has_key(instrument)

    def GetTradeableInstruments(self):
    	for instrument in self.apiData.GetAllInstrumentsTradeable()['instruments']:
            if instrument['type'] != 'METAL' and instrument['type'] != 'CFD' and instrument['name'] != 'USD_SAR':
        		self.Add(instrument['name'],
        			{
        				'min': instrument['minimumTradeSize'],
        				'precision': instrument['tradeUnitsPrecision'],
        				'rate': int(1 / float(instrument['marginRate'])),
        				'max': instrument['maximumOrderUnits']
        			}
        		)

    def GetPrecision(self, instrument):
        return self.instruments[instrument]['precision'];
