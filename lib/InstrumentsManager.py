

class InstrumentsManager(object):

    transactions = {}

    def __init__(self, transactions = {}):
        self.transactions = transactions

    def Add(self, instrument, data):
    	self.transactions[instrument] = data;

    def ExistsInstrument(self, instrument):
        return self.transactions.has_key(instrument)