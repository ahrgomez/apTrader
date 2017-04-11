from lib.ApiData import ApiData

class InstrumentsManager(object):

    instruments = {}
    apiData = {}

    def __init__(self, instruments = {}):
        self.instruments = instruments
        self.apiData = ApiData()
        self.GetTradeableInstruments()

    def Add(self, instrument, data):
    	self.instruments[instrument] = data;

    def ExistsInstrument(self, instrument):
        return self.instruments.has_key(instrument)

    def GetTradeableInstruments(self):
    	for instrument in self.apiData.GetAllInstrumentsTradeable()['instruments']:
            if (
                instrument['type'] != 'METAL'
                and instrument['type'] != 'CFD'
                and ('SAR' not in instrument['name'])
                and ('INR' not in instrument['name'])
                and ('CNH' not in instrument['name'])
                and ('THB' not in instrument['name'])
                and ('MXN' not in instrument['name'])
                and ('DKK' not in instrument['name'])
            ):
                self.Add(instrument['name'],
                	{
                		'min': instrument['minimumTradeSize'],
                		'precision': instrument['tradeUnitsPrecision'],
                        'pricePrecision': instrument['displayPrecision'],
                		'rate': int(1 / float(instrument['marginRate'])),
                        'pipLocation': int(instrument['pipLocation']),
                		'max': instrument['maximumOrderUnits']
                	}
                );

    def GetPrecision(self, instrument):
        return self.instruments[instrument]['precision'];
