regattaApp.controller('EventsController', ['$scope','$http',
  function ($scope,$http) {

    $scope.events = [];

    $http.get('/api/events').success( function(data){
      $scope.events = data;
    });

    $scope.orderEvent = function(event) {
        return parseInt(event.eventNumber);
    };

    $scope.orderByLane = function(race) {
        return parseInt(race.laneNumber);
    };

}]);
