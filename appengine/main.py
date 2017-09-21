"""Main.py is the top level script.

Loads the Bottle framework and mounts controllers.  Also adds a custom error
handler.
"""

from google.appengine.api import memcache, urlfetch

# import the Bottle framework
from server.lib.bottle import Bottle, request, response, template

import json, logging, StringIO, urllib2, sys
from decimal import *

# TODO: name and list your controllers here so their routes become accessible.
from server.controllers import RESOURCE_NAME_controller

import hashlib, hmac, time # for bitcoinaverage API
import config # this file contains secret API key(s), and so it is in .gitignore

BLOCKEXPLORER_URL = 'http://chainz.cryptoid.info/meow/api.dws?q=getbalance&a='
TRADING_PAIR_URL_CRYPTOPIA = 'https://www.cryptopia.co.nz/api/GetMarket/'
BTER_LTC_BTC_URL = 'http://data.bter.com/api/1/ticker/ltc_btc'

TIMEOUT_DEADLINE = 10 # seconds

# used for BTC / (CNY, GBP, EUR, AUD)
def bitcoinaverage_ticker(currency):
  timestamp = int(time.time())
  payload = '{}.{}'.format(timestamp, config.bitcoinaverage_public_key)
  hex_hash = hmac.new(config.bitcoinaverage_secret_key.encode(), msg=payload.encode(), digestmod=hashlib.sha256).hexdigest()
  signature = '{}.{}'.format(payload, hex_hash)

  url = 'https://apiv2.bitcoinaverage.com/indices/global/ticker/BTC' + currency
  headers = {'X-Signature': signature}
  return urlfetch.fetch(url, headers=headers, deadline=TIMEOUT_DEADLINE)

def cryptopia_ticker(currency1, currency2):
  url = TRADING_PAIR_URL_CRYPTOPIA + currency1 + '_' + currency2
  return urlfetch.fetch(url, deadline=TIMEOUT_DEADLINE)

# Run the Bottle wsgi application. We don't need to call run() since our
# application is embedded within an App Engine WSGI application server.
bottle = Bottle()

# Mount a new instance of bottle for each controller and URL prefix.
# TODO: Change 'RESOURCE_NAME' and add new controller references
bottle.mount("/RESOURCE_NAME", RESOURCE_NAME_controller.bottle)

@bottle.route('/')
def home():
  """Return project name at application root URL"""
  return "KittehCoin Balance"

@bottle.route('/api/balance/<address:re:[a-zA-Z0-9]+>')
def getBalance(address=''):
  response.content_type = 'application/json; charset=utf-8'

  url = BLOCKEXPLORER_URL + address
  data = urlfetch.fetch(url, deadline=TIMEOUT_DEADLINE)
  if (not data or not data.content or data.status_code != 200):
    logging.warn('No content returned from ' + url + ': ' + str(data))

  dataDict = json.loads(data.content)
  balance = json.dumps(dataDict)
  mReturn = balance

  query = request.query.decode()
  if (len(query) > 0):
    mReturn = query['callback'] + '({balance:' + balance + '})'

  logging.info("getBalance(" + address + "): " + mReturn)
  return mReturn

@bottle.route('/api/trading-meow')
@bottle.route('/api/trading-meow/')
@bottle.route('/api/trading-meow/<currency:re:[A-Z][A-Z][A-Z]>')
def tradingMEOW(currency='LTC'):
    response.content_type = 'application/json; charset=utf-8'

    mReturn = '{}'
    meowLtc = json.loads(memcache.get('trading_MEOW_LTC'))
    if (not meowLtc):
        logging.warn("No data found in memcache for trading_MEOW_LTC")
        return mReturn

    ltcBtc = json.loads(memcache.get('trading_LTC_BTC'))
    if (not ltcBtc and currency != 'LTC'):
        logging.warn("No data found in memcache for trading_LTC_BTC")
        return mReturn

    if (currency not in ['LTC', 'BTC']):
        btcCurrency = json.loads(memcache.get('trading_BTC_' + currency))
        if (not btcCurrency):
            logging.warn("No data found in memcache for trading_BTC_" + currency)
            return mReturn
        # MEOW -> LTC -> BTC -> FIAT
        mReturn = '%.10f' % (Decimal(meowLtc['price']) * Decimal(ltcBtc['price']) * Decimal(btcCurrency['price']))
    elif (currency == 'BTC'):
        # MEOW -> LTC -> BTC
        mReturn = '%.10f' % (Decimal(meowLtc['price']) * Decimal(ltcBtc['price']))
    else:
        mReturn = meowLtc['price']

    query = request.query.decode()
    if (len(query) > 0):
        mReturn = query['callback'] + '({price:' + str(mReturn) + '})'

    logging.info("tradingMEOW(" + currency + "): " + str(mReturn))
    return str(mReturn)

def pullTradingPair(currency1='MEOW', currency2='LTC'):
  dataDict = None
  useBackupUrl = False
  logging.info('trading pair: ' + currency1 + '_' + currency2)

  try:
    if (currency1 == 'BTC' and currency2 in ['CNY', 'EUR', 'GBP', 'USD', 'AUD']):
      data = bitcoinaverage_ticker(currency2)
      if (not data or not data.content or data.status_code != 200):
        logging.warn('No content returned from ' + url)
        useBackupUrl = True
      else:
        dataDict = json.loads(data.content)
        dataDict['price'] = dataDict['last']
    else:
      data = cryptopia_ticker(currency1, currency2)
      if (not data or not data.content or data.status_code != 200):
        logging.warn('No content returned from ' + url)
        useBackupUrl = True
      else:
        dataDict = json.loads(data.content)
        dataDict['price'] = dataDict['Data']['LastPrice']

  except:
    logging.warn('Error retrieving data for ' + currency1 + '_' + currency2)
    useBackupUrl = True

  if (useBackupUrl and currency1 == 'LTC' and currency2 == 'BTC'):
    backupUrl = BTER_LTC_BTC_URL
    logging.warn('Now trying ' + backupUrl)
    data = urlfetch.fetch(backupUrl, deadline=TIMEOUT_DEADLINE)
    dataDict = json.loads(data.content)
    dataDict['price'] = dataDict['last']

  tradingData = json.dumps(dataDict)

  memcache.set('trading_' + currency1 + '_' + currency2, tradingData)
  logging.info('Stored in memcache for key trading_' + currency1 + '_' + currency2 + ': ' + tradingData)

@bottle.route('/tasks/pull-cryptocoincharts-data')
def pullCryptocoinchartsData():
    pullTradingPair('MEOW', 'LTC')
    pullTradingPair('LTC', 'BTC')
    pullTradingPair('BTC', 'USD')
    pullTradingPair('BTC', 'EUR')
    pullTradingPair('BTC', 'GBP')
    pullTradingPair('BTC', 'CNY')
    return "Done"

@bottle.error(404)
def error_404(error):
  """Return a custom 404 error."""
  return 'Sorry, Nothing at this URL.'
