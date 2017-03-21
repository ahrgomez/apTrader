

class TransactionsManager(object):

    transactions = {}

    def __init__(self, transactions = {}):
        self.transactions = transactions

    def AddTransaction(self, instrument, order_id, stop_loss, take_profit):
    	self.transactions[instrument] = { 'order_id': order_id, 'stop_loss': stop_loss, 'take_profit': take_profit }

    def RemoveTransaction(self, instrument):
    	self.transactions.pop(instrument, None)

    def UpdateTransaction(self, instrument, order_id, stop_loss, take_profit):
    	self.transactions[instrument] = { 'order_id': order_id, 'stop_loss': stop_loss, 'take_profit': take_profit }