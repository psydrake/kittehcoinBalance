'use strict';

angular.module('app.controllers', []).
    controller('addController', function($location, $log, $scope, settingsService, utilService, customService) {
		$scope.wallet = {label:'', address:''};

		$scope.cancel = function() {
			$location.path('/edit');
		}

		$scope.save = function() {
			var wallets = settingsService.getObject('wallets');

			// do some simple validation
			$scope.errors = [];
			var error = utilService.validateWallet($scope.wallet, wallets);
			if (error) {
				$scope.errors.push(error);
			}
			else { // no errors, let's add new wallet and redirect to home
				wallets.push($scope.wallet);

				// save wallets to local storage
				settingsService.setObject('wallets', wallets);
				$location.path('/home');
			}
		}

		customService.trackPage('/add');
    }).
	controller('editController', function($scope, $location, $log, settingsService, utilService) {
		$scope.wallets = settingsService.getObject('wallets');

		$scope.cancel = function() {
			$location.path('/home');
		}

		$scope.remove = function(index) {
			$scope.wallets.splice(index, 1);
			$log.info('wallets:', $scope.wallets);
		}

		$scope.add = function() {
			// Don't let user go to "Add Wallet" page if there are unsaved changes on page
			// NOTE: _.isEqual($scope.wallets, savedWallets)) doesn't always work, due to $hashkey
			var hasUnsavedChanges = false;
			var savedWallets = settingsService.getObject('wallets');

			if (savedWallets.length !== $scope.wallets.length) {
				hasUnsavedChanges = true;
			}
			else {
				for (var i=0; i<savedWallets.length; i++) {
					if (savedWallets[i].address !== $scope.wallets[i].address ||
						savedWallets[i].label !== $scope.wallets[i].label) {
						hasUnsavedChanges = true;
						break;
					}
				}
			}

			if (hasUnsavedChanges) {
				$scope.errors = ['You have unsaved changes. Please save or cancel before adding a new wallet.'];
			}
			else {
				$location.path('/add');
			}
		}

		$scope.save = function() {
			// do some basic validation
			$scope.errors = [];
			for (var i=0; i < $scope.wallets.length; i++) {
				var error = utilService.validateWallet($scope.wallets[i]);
				if (error) {
					$scope.errors.push(error);
				}
			}

			if ($scope.errors.length > 0) { // if errors, remove duplicates
				$scope.errors = _.uniq($scope.errors, false)
			}
			else { // if no errors, save wallets and redirect to home
				settingsService.setObject('wallets', $scope.wallets);
				$location.path('/home');
			}
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



