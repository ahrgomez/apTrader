
from lib import ApiData, InstrumentsManager

access_token = '362c69e15045ab046662317d02837de5-abe03f3f1c7b18419930866fe2bd69b0'
account_id = '101-004-5177797-001'

apiData = ApiData.ApiData(account_id, access_token)
instrumentsManager = InstrumentsManager.InstrumentsManager()

def main():
	GetTradeableInstruments()
	for inst in instrumentsManager.transactions:
		print inst + ": " + str(instrumentsManager.transactions[inst])

def GetTradeableInstruments():
	for instrument in apiData.GetAllInstrumentsTradeable()['instruments']:
		instrumentsManager.Add(instrument['name'], instrument
			#{
				#'min': instrument['minimumTradeSize'],
				#'precision': instrument['displayPrecision'],
				#'rate': int(1 / float(instrument['marginRate'])),
				#'max': instrument['maximumOrderUnits']
			#}
		)

if __name__ == "__main__":
    main()
