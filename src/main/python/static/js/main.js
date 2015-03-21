var regattaApp = angular.module('regattaApp', ['ngRoute']);

regattaApp.config(['$routeProvider',
  function($routeProvider) {
    $routeProvider.
      when('/home', {
        templateUrl: '../templates/home.html',
        controller: 'HomeController'
      }).
      when('/login', {
        templateUrl: '../templates/login.html',
        controller: 'LoginController'
      }).
            when('/login', {
              templateUrl: '../templates/register.html',
              controller: 'RegisterController'
            }).
        when('/view/events', {
          templateUrl: '../templates/events.html',
          controller: 'EventsController'
        }).
      when('/view/teams', {
          templateUrl: '../templates/teams.html',
          controller: 'TeamController'
        }).
      when('/view/boats', {
          templateUrl: '../templates/boats.html',
          controller: 'BoatController'
        }).
                  when('/manage/start_race', {
                                     templateUrl: '../templates/start.html',
                                     controller: 'StartRaceController'
                                   }).
          when('/manage/finish_race', {
                             templateUrl: '../templates/finish.html',
                             controller: 'FinishRaceController'
                           }).
         when('/manage/lanes', {
             templateUrl: '../templates/lane_assignment.html',
             controller: 'LaneController'
           }).
        when('/admin/load', {
          templateUrl: '../templates/load.html',
          controller: 'LoadController'
        }).
      otherwise({
        redirectTo: '/home'
      });
  }]);

regattaApp.controller('LoginController', ['$scope',
    function ($scope) {
        $scope.name = 'Hello community';
    }]);

regattaApp.controller('LoginController', ['$scope',
    function ($scope) {
        $scope.name = 'Hello community';
    }]);


regattaApp.controller('HomeController', ['$scope',
    function ($scope) {
    }]);

regattaApp.controller('EventsController', ['$http',
    function ($http) {
        var event = this;
        event.events = [];

        $http.get('/api/events').success( function(data){
            event.events = data;
        });
    }]);

regattaApp.controller('BoatController', ['$scope',  '$http',
    function ($scope,$http) {
        var boat = this;
        boat.events = [];
        boat.eventList = [];

        $http.get('/api/boats').success( function(data){
            boat.events = data;
            boat.eventList = _.map(_.unique(_.pluck(boat.events,'Event')), function(event){ return { label:event, value: event }; });
            console.log(boat.eventList);
        });

        $scope.criteriaMatch = function( criteria ) {
          return function( item ) {
            //console.log('in match '+criteria+' '+item.Event);
            //console.log(item.Event == criteria);
            return item.Event == criteria;
          };
        };
    }]);
regattaApp.controller('TeamController', ['$http',
    function ($http) {
        var team = this;
        team.teams = [];

        $http.get('/api/teams').success( function(data){
            team.teams = data;
        });
    }]);

regattaApp.controller('FinishRaceController', ['$scope','$http',
    function ($scope,$http) {
        var event = this;
        event.selected_events = [];
        event.events = [];
        event.eventList = [];
        event.filtered_events = [];
        event.finishes = [];
        event.finisher = 0;
        event.selectedEvent = 1;

        $http.get('/api/boats').success( function(data){
            event.events = data;
            event.eventList = _.map(_.unique(_.pluck(data,'Event')), function(event){ return { label:event, value: event }; });
        });

        $scope.onFilterEvents = function(event_num){
            //console.log(event.events);
            //console.log(typeof event_num);
            event.filtered_events = _.where(event.events, {Event: parseInt(event_num)});
            event.filtered_events = _.map(event.filtered_events, function(entry) { return _.extend(entry, {finish_order: "DNF"}); });

            console.log(event.filtered_events.length)
            event.remaining_lanes = new Array(event.filtered_events.length)
                                        .join().split(',')
                                        .map(function(item, index){ return ++index;});
            console.log(event.filtered_events);
        };

        $scope.onAssignTimes = function(assigned_lanes){
            console.log(assigned_lanes);
            console.log($scope.assigned_lanes);

        };
        $scope.onAssignLane = function(assigned_lanes){
            console.log(assigned_lanes);
        };
        $scope.onFinish = function(){
            event.finisher += 1;
            event.finishes.push({finish_time: Date.now(), finish_order: event.finisher, finish_lane: 0});
            console.log(event.finishes);
        };

        $scope.onReset = function(){
            event.finisher = 0;
            event.finishes = [];
        };

        $scope.criteriaMatch = function( criteria ) {
          return function( item ) {
            //console.log('in match '+criteria+' '+item.Event);
            //console.log(item.Event == criteria);
            return item.Event == criteria;
          };
        };
    }]);

regattaApp.controller('StartRaceController', ['$http','$scope',
    function($http,$scope){
            var event = this;
            event.events = [];
            event.eventList = [];
            event.filtered_event = [];
            event.postStatus = "";

            $http.get('/api/events').success( function(data){
                event.events = data;
                event.eventList = _.map(_.unique(_.pluck(data,'Event')), function(event){ return { label:event, value: event }; });

            });
           $scope.onFilterEvents = function(event_num){
                event.filtered_event = _.where(event.events, {Event: parseInt(event_num)});
                event.postStatus = "";

            };

           $scope.onFinish = function(){
                event.finish_time = Date.now()
                event.postStatus = "";

           };
           $scope.onReset = function(){
               event.finish_time = "";
               event.postStatus = "";
              // $scope.selectedEvent = "";

           }

           $scope.onPost = function(event_num){
                $http.post('api/start', {event: parseInt(event_num), start_time: event.finish_time}).
                success(function(data, status, headers, config) {
                 // this callback will be called asynchronously
                 // when the response is available
                 console.log(status);
                 event.postStatus = 'POST SUCCESSFUL';
               }).
               error(function(data, status, headers, config) {
                event.postStatus = "POST FAILED";
                console.log(status);
               });
           }
    }
    ]);

regattaApp.controller('LaneController', ['$http',
            function ($http) {
                var event = this;
                event.events = [];

                $scope.onLaneAssignment = function(){
                    $http.post('/api/assignlanes').success(function(data){
                        console.log('setting lane assigments');
                        $http.get('/api/boats').success( function(data){
                            event.events = data;
                        });
                    })
                }

                $http.get('/api/teams').success( function(data){
                    team.teams = data;
                });
            }]);

regattaApp.controller('RegisterController', ['$http','$scope',
    function ($http,$scope) {
        var registration = this;

        $scope.onRegister = function(){
            console.log("pass "+$scope.password1);
            if ( $scope.password1 != $scope.password2 ){
                registration.error = "Passwords dont match";
            }
            else {
                $http.post('/api/user', { first: $scope.first, last: $scope.last }).success(function(data){
                    console.log('setting lane assigments');
                })
            }
        }

    }]);