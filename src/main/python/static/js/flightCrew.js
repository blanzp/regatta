regattaApp.controller('FlightCrewController', ['$scope','$http','$routeParams',
  function ($scope,$http,$routeParams) {

    $scope.crews = [];
    $scope.flights = [];
    $scope.event_id = $routeParams.event_id;
    $scope.eventTitle = "";
    $scope.crew_dict = {};


    $http.get('/api/events/'+ $routeParams.event_id).success( function(data){
      $scope.crews = data.crew;
      $scope.flights = data.stage[0].race;
      $scope.eventTitle = data.eventTitle;

      for ( i = 0; i<data.crew.length; i++ ){
        tmp_crew = data.crew[i];
        $scope.crew_dict[tmp_crew._id] = tmp_crew.organization;
      }

    });
}]);
