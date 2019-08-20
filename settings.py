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

ACCESS_TOKEN = '9fda2fa183e2697b9f89452911e31b88-cfb85ddcaceaeb3295d62e2934cf85ac'
ACCOUNT_ID = '101-004-12006472-001'

BASE_CURRENCY = "EUR"
