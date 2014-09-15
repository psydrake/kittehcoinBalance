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

BLOCKEXPLORER_URL = 'http://kittehcoinblockexplorer.com/chain/Kittehcoin/q/addressbalance/'
BLOCKEXPLORER_URL_BACKUP = 'http://kitexplorer.tk/chain/Kittehcoin/q/addressbalance/'
TRADING_PAIR_URL = 'http://www.cryptocoincharts.info/v2/api/tradingPair/'
TRADING_PAIR_URL_CRYPTSY = 'http://pubapi.cryptsy.com/api.php?method=singlemarketdata&marketid=231'
TRADING_PAIR_URL_USD_BACKUP = 'https://coinbase.com/api/v1/prices/buy' 
BTER_LTC_BTC_URL = 'http://data.bter.com/api/1/ticker/ltc_btc'
BTCAVERAGE_URL = 'https://api.bitcoinaverage.com/ticker/' # used for BTC / (CNY, EUR, GBP, AUD)

TIMEOUT_DEADLINE = 10 # seconds

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
    data = None
    useBackupUrl = False

    try:
        data = urlfetch.fetch(url, deadline=TIMEOUT_DEADLINE)
        if (not data or not data.content or data.status_code != 200):
            logging.warn('No content returned from ' + url)
            useBackupUrl = True
    except:
        logging.warn('Error retrieving ' + url)
        useBackupUrl = True

    if (useBackupUrl):
        backupUrl = BLOCKEXPLORER_URL_BACKUP + address
        logging.warn('Now trying ' + backupUrl)
        data = urlfetch.fetch(backupUrl, deadline=TIMEOUT_DEADLINE)

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
    # temporarily commenting out TRADING_PAIR_URL (cryptocoincharts.info) url, since they apparently changed their API
    # relying on backup URLs
    url = TRADING_PAIR_URL_CRYPTSY if (currency1 == 'MEOW' and currency2 == 'LTC') else ''  #TRADING_PAIR_URL + currency1 + '_' + currency2
    data = None
    useBackupUrl = False

    logging.info('trading pair: ' + currency1 + '_' + currency2 + ', url: ' + url)
    try:
        data = urlfetch.fetch(url, deadline=TIMEOUT_DEADLINE)
        if (not data or not data.content or data.status_code != 200):
            logging.warn('No content returned from ' + url)
            useBackupUrl = True
    except:
        logging.warn('Error retrieving ' + url)
        useBackupUrl = True

    if (useBackupUrl):
        backupUrl = ''
        if (currency1 == 'LTC' and currency2 == 'BTC'):
            backupUrl = BTER_LTC_BTC_URL
        elif (currency1 == 'BTC' and currency2 == 'USD'):
            backupUrl = TRADING_PAIR_URL_USD_BACKUP
        elif (currency1 == 'BTC' and currency2 in ['CNY', 'EUR', 'GBP', 'AUD']):
            backupUrl = BTCAVERAGE_URL + currency2 + '/'
        else:
            logging.error('Cannot get trading pair for ' + currency1 + ' / ' + currency2)
            return

        logging.warn('Now trying ' + backupUrl)
        data = urlfetch.fetch(backupUrl, deadline=TIMEOUT_DEADLINE)

    dataDict = json.loads(data.content)

    if (useBackupUrl):
        if (currency1 == 'BTC' and currency2 == 'USD'):
            if (dataDict['subtotal']['currency'] == 'USD'):
                dataDict = {'price': dataDict['subtotal']['amount']}
                logging.info('BTC_USD: ' + dataDict['price'])
            else:
                logging.error('Unexpected JSON returned from URL ' + TRADING_PAIR_URL_USD_BACKUP)
                return
        elif ((currency1 == 'BTC' and currency2 in ['CNY', 'EUR', 'GBP', 'AUD']) \
            or (currency1 == 'LTC' and currency2 == 'BTC')):
            dataDict['price'] = dataDict['last']
        else:
            logging.error('Error loading trading pair from ' + url)
            return

    elif ((currency1 == 'BTC' and currency2 in ['CNY', 'EUR', 'GBP', 'USD', 'AUD']) \
        or (currency1 == 'LTC' and currency2 == 'BTC')):
        # standardize format of exchange rate data from different APIs (we will use 'price' as a key)      
        if (not dataDict['price'] and dataDict['last']):
            dataDict['price'] = dataDict['last'] 

    elif (currency1 == 'MEOW' and currency2 == 'LTC'):
        if (dataDict['return']['markets']['MEOW']['label'] == "MEOW/LTC"):
            dataDict = {'price': dataDict['return']['markets']['MEOW']['lasttradeprice']}
            logging.info('MEOW_LTC: ' + dataDict['price'])
        else:
            logging.error('Cannot get trading pair for ' + currency1 + ' / ' + currency2)
            return

    tradingData = json.dumps(dataDict)

    memcache.set('trading_' + currency1 + '_' + currency2, tradingData)
    logging.info('Stored in memcache for key trading_' + currency1 + '_' + currency2 + ': ' + tradingData)

@bottle.route('/tasks/pull-cryptocoincharts-data')
def pullCryptocoinchartsData():
    pullTradingPair('MEOW', 'LTC')
    pullTradingPair('LTC', 'BTC')
    pullTradingPair('BTC', 'USD')
    pullTradingPair('BTC', 'EUR')
    #pullTradingPair('BTC', 'GBP')
    pullTradingPair('BTC', 'CNY')
    return "Done"

@bottle.error(404)
def error_404(error):
  """Return a custom 404 error."""
  return 'Sorry, Nothing at this URL.'
