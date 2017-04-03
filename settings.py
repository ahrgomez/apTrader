import os

ENVIRONMENTS = {
    "streaming": {
        "real": "stream-fxtrade.oanda.com",
        "practice": "stream-fxpractice.oanda.com",
        "sandbox": "stream-sandbox.oanda.com"
    },
    "api": {
        "real": "api-fxtrade.oanda.com",
        "practice": "api-fxpractice.oanda.com",
        "sandbox": "api-sandbox.oanda.com"
    }
}

MODE = "practice"

STREAM_DOMAIN = ENVIRONMENTS["streaming"][MODE]
API_DOMAIN = ENVIRONMENTS["api"][MODE]

ACCESS_TOKEN = '362c69e15045ab046662317d02837de5-abe03f3f1c7b18419930866fe2bd69b0'
ACCOUNT_ID = '101-004-5177797-001'

BASE_CURRENCY = "EUR"
