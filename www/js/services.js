'use strict';

// Demonstrate how to register services
// In this case it is a simple value service.
angular.module('app.services', []).
    factory('utilService', function() {
        return {
            // from: http://www.xe.com/symbols.php
            currencyMap: {
				"BTC": "฿",
                "LTC": "Ł",
                "USD": "$",
                "GBP": "£",
                "DKK": "kr",
                "CAD": "$",
                "MXN": "$",
                "SEK": "kr",
                "SGD": "$",
                "HKD": "$",
                "AUD": "$",
                "CHF": "CHF",
                "CNY": "¥",
                "NZD": "$",
                "THB": "฿",
                "EUR": "€",
                "ARS": "$",
                "NOK": "kr",
                "RUB": "руб",
                "JPY": "¥",
                "CZK": "Kč",
                "BRL": "R$",
                "PLN": "zł",
                "ZAR": "R"
            },

            currencySymbol: function(code) {
                var symbol = this.currencyMap[code];
                //console.log('code:', code, 'symbol:', symbol);
                return symbol ? symbol : '';
            },

			getCurrencyAbbrev: function(symbol) {
				if (symbol && symbol.length > 3) {
					return symbol.substr(symbol.length - 3);
				}
				else {
					return '';
				}
			},

			getPriceCompareClass: function(price1, price2) {
				if (!price1 || !price2) {
					return 'priceUnknown';
				}
				else if (price1 > price2) {
					return 'priceUp';
				}
				else if (price1 < price2) {
					return 'priceDown';
				}
				else {
					return 'priceSame';
				}
			},

			getAppVersion: function() {
				return '1.0.1'; // version
			}
        }
    }).
	factory('settingsService', function($log) {
		return {
			store: null, // store is the Persist.js local storage store

			setStore: function(theStore) {
				this.store = theStore;
			},

			// get a JavaScript object by key
			getObject: function(key) {
				var obj = '';
				if (key && this.store) {
					var strObj = this.store.get(key);
					obj = JSON.parse(strObj);
					if (key === 'wallets' && !obj) {
						obj = []; // return empty list if no wallets have been saved
					}
				}
				$log.info('getObject(). key:', key, ', value:', obj);
				return obj;
			},

			setObject: function(key, value) {
				if (key && this.store) {
					this.store.set(key, JSON.stringify(value));
				}
			},

			// get String value by key
            getValue: function(key) {
				var value = '';
				if (key === 'preferredCurrency') {
					value = 'USD'; // default - this is overwritten by what is in store
				}
                if (this.store && this.store.get(key)) {
                    value = this.store.get(key);
                }
                return value;
            },

            setValue: function(key, value) {
                if (key && this.store) {
                    this.store.set(key, value);
                }
            },

            // get a number value by key - defaults to zero if not found in local storage
            getNumValue: function(key) {
                var value = 0;
                if (this.store && this.store.get(key)) {
                    value = Number(this.store.get(key));
                }
                return value;
            },

            // set a number value by key
            setNumValue: function(key, value) {
                if (this.store) {
                    this.store.set(key, value);
                }
            },

            symbols: ['BTC', 'CNY', 'EUR', 'USD']
        }
    }).
    factory('cryptocoinchartsAPIService', function($http, $log, utilService) {
        var cccAPI = {};

        cccAPI.convert = function(currency, balance) {
			var url = 'http://kittehcoinbalance.appspot.com/api/trading-meow/';

            if (currency) {
		        url = url + currency;
            }

            return {
                success: function(fn) {
					//$log.info('in success! fn:', fn);
					$http.jsonp(url + '?callback=JSON_CALLBACK').success(function(data, status, headers, config) {
						var price  = data['price'];
						$log.info('got price for currency', currency, ':', price);
						fn(Number(price) * Number(balance));
					});
                }
            };
        }

        return cccAPI;
  }).
  factory('blockexplorerAPIService', function($http, $log, utilService) {
        var beAPI = {};

        beAPI.getBalance = function(address) {
			var url = 'http://kittehcoinbalance.appspot.com/api/balance/';

            if (address) {
		        url = url + address;
            }

            return {
                success: function(fn) {
					$http.jsonp(url + '?callback=JSON_CALLBACK').success(function(data) {
						$log.info('jsonp result:', data);
					    fn(data['balance']);
					}).error(function(data, status, headers, config) {
						$log.warn('error! data:', data, ', status:', status, ', headers:', headers, ', config:', config);
						fn(0, true); 
					});
                }
            };
        }

        return beAPI;
  });

