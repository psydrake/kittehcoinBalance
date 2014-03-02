# KittehCoin Balance

## About
Simple web / mobile app for checking the balance of your KittehCoin wallet address(es).

## Technical
KittehCoin Balance consists of two parts:
* A pure HTML / CSS / JavaScript front end built with the [AngularJS](http://angularjs.org/) JavaScript framework.
* A [Google App Engine](https://developers.google.com/appengine/) back end, written in [Python](http://www.python.org/), that looks up wallet balance data from the [Kitteh Coin Block Explorer](http://kittehcoinblockexplorer.com/) and caches currency price data from the [cryptocoincharts.info](http://www.cryptocoincharts.info/) API.

The front end communicates with the back end via [JSONP](http://en.wikipedia.org/wiki/JSONP) calls. The backend polls cryptocoincharts.info every 10 minutes, and it stores this data in [memcache](https://developers.google.com/appengine/docs/python/memcache/) for all subsequent client requests, in order to reduce load on the CryptoCoinCharts server. Wallet balance lookups from the Kitteh Coin Block Explorer [API](http://kittehcoinblockexplorer.com/chain/Kittehcoin/q) occur on demand.

## Install On Your Device
* [KittehCoin Balance for Android](https://play.google.com/store/apps/details?id=net.edrake.kittehcoinbalance)
* [KittehCoin Balance in the Chrome Web Store](https://chrome.google.com/webstore/detail/kittehcoin-balance/ijhkeggnlfaafnjfmddgjfmlchpofggo)
* [KittehCoin Balance as a Web Site](http://d2f04lgzuo9226.cloudfront.net/main.html)

## Logo
The KittehCoin Balance [logo](http://d2f04lgzuo9226.cloudfront.net/img/kittehcoinBalance_logo_1536.png) 
is modified from an [image](http://commons.wikimedia.org/wiki/File:Green-emblem-scales.svg)
licensed under the [Creative Commons Attribution-Share Alike 2.5 Generic](http://creativecommons.org/licenses/by-sa/2.5/deed.en)
license, originally modified by [Danieldnm](http://commons.wikimedia.org/wiki/User:Danieldnm).

## Author
Drake Emko - drakee (a) gmail.com
* [@DrakeEmko](https://twitter.com/DrakeEmko)
* [Wolfgirl Band](http://wolfgirl.bandcamp.com/)
