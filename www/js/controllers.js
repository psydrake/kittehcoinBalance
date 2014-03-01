'use strict';

angular.module('app.controllers', []).
    controller('addController', function($location, $log, $scope, settingsService, utilService, customService) {
		$scope.wallet = {label:'', address:''};

		$scope.save = function() {
			$log.info('in save():', $scope.wallet);
			var wallets = settingsService.getObject('wallets');

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

		$scope.remove = function(index) {
			$scope.wallets.splice(index, 1);
			$log.info('wallets:', $scope.wallets);
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
		$scope.data = {
			total: 0, 
			convertedTotal: 0, 
			currency: settingsService.getValue('preferredCurrency'),
			wallets: settingsService.getObject('wallets')
		};

		if (!$scope.data.wallets || $scope.data.wallets.length === 0) {
			$log.info('no wallets, go to addWallet');
			$location.path('/add');
		}

        $scope.loadData = function() {
			angular.forEach($scope.data.wallets, function(wallet) {
				blockexplorerAPIService.getBalance(wallet.address).success(function (balance, isError) {
					if (isError) {
						wallet.error = 'Error - is wallet address correct?';
					}
					wallet.balance = Number(balance);
					$log.info('balance for', wallet.address, 'is', wallet.balance);
					$scope.data.total += wallet.balance;

					cryptocoinchartsAPIService.convert($scope.data.currency, wallet.balance).success(function(price) {
						$scope.data.convertedTotal += Number(price);
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
		$scope.data = {
			preferredCurrency: settingsService.getValue('preferredCurrency'),
			symbols: settingsService.symbols
		};

		$scope.$watch('data.preferredCurrency', function() {
			settingsService.setValue('preferredCurrency', $scope.data.preferredCurrency);
			$log.info('Set preferred currency to', settingsService.getValue('preferredCurrency'));
		});

		customService.trackPage('/settings');
    }).
    controller('aboutController', function($scope, utilService, customService) {
		$scope.data = {version: utilService.getAppVersion()};

		customService.trackPage('/about');
    });



