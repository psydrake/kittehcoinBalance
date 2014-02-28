'use strict';

angular.module('app.controllers', []).
    controller('addController', function($location, $log, $scope, settingsService, utilService, customService) {
		$scope.wallet = {label:'', address:''};

		$scope.save = function() {
			$log.info('in save():', $scope.wallet);
			var wallets = settingsService.getObject('wallets');
			if (!wallets) {
				wallets = [];
			}

			wallets.push($scope.wallet);
			$log.info('wallets:', wallets);
			
			// save wallets to local storage
			settingsService.setObject('wallets', wallets);
			$location.path('/home');
		}

		customService.trackPage('/add');
    }).
	controller('editController', function($scope, $location, $log, settingsService) {
		$scope.wallets = settingsService.getObject('wallets');
		if (!$scope.wallets) {
			$scope.wallets = [];
		}

		$scope.remove = function(index) {
			$scope.wallets.splice(index, 1);
			$log.info('wallets:', $scope.wallets);
			settingsService.setObject('wallets', $scope.wallets);
		}

		$scope.add = function() {
			$log.info('add wallet');
			$location.path('/add');
		}

		$scope.save = function() {
			settingsService.setObject('wallets', $scope.wallets);
			$location.path('/home');
		}
	}).
    controller('homeController', function($scope, $rootScope, $location, $log, blockexplorerAPIService, cryptocoinchartsAPIService, utilService, settingsService, customService) {
		$scope.wallets = settingsService.getObject('wallets');

		if (!$scope.wallets || $scope.wallets.length === 0) {
			$log.info('no wallets, go to addWallet');
			$location.path('/add');
		}

        $scope.loadData = function() {
			$scope.balanceTotal = 0;
			$scope.convertedBalanceTotal = 0;
			$scope.currency = settingsService.getValue('preferredCurrency');
			
			angular.forEach($scope.wallets, function(wallet) {
				blockexplorerAPIService.getBalance(wallet.address).success(function (balance, isError) {
					if (isError) {
						wallet.error = 'Error - is wallet address correct?';
					}
					wallet.balance = Number(balance);
					$log.info('balance for', wallet.address, 'is', wallet.balance);
					$scope.balanceTotal += wallet.balance;

					cryptocoinchartsAPIService.convert($scope.currency, wallet.balance).success(function(price) {
						$scope.convertedBalanceTotal += Number(price);
					});
				});
			});
		}

        $scope.$on('refresh', function(event, path) {
            if (path && path === '/home') {
                $scope.loadData();
            }
        });

        $rootScope.loadData();

		customService.trackPage('/home');
    }).
    controller('settingsController', function($scope, $rootScope, $log, settingsService, customService) {
		$scope.preferredCurrency = settingsService.getValue('preferredCurrency');

		$scope.$watch('preferredCurrency', function() {
			settingsService.setValue('preferredCurrency', $scope.preferredCurrency);
			$log.info('Set preferred currency to', settingsService.getValue('preferredCurrency'));
		});

		$scope.symbols = settingsService.symbols;

		customService.trackPage('/settings');
    }).
    controller('aboutController', function($scope, utilService, customService) {
		$scope.version = utilService.getAppVersion();

		customService.trackPage('/about');
    });



