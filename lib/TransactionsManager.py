

class TransactionsManager(object):

    transactions = {}

    def __init__(self, transactions = {}):
        self.transactions = transactions

    def AddTransaction(self, instrument, order_id, stop_loss):
    	self.transactions[instrument] = { 'order_id': order_id, 'stop_loss': stop_loss }

    def RemoveTransaction(self, instrument):
    	self.transactions.pop(instrument, None)

    def UpdateTransaction(self, instrument, order_id, stop_loss):
    	self.transactions[instrument] = { 'order_id': order_id, 'stop_loss': stop_loss }
