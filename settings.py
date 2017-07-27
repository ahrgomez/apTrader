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

ACCESS_TOKEN = '4c1736658b27f079c118c283c0c1849f-0fee3fc60d393e3cead87aea08fbf351'
ACCOUNT_ID = '101-004-6464985-001'

BASE_CURRENCY = "EUR"
