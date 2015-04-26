
//angular.module('Authentication', []);
//angular.module('Home', []);

var regattaApp = angular.module('regattaApp', ['ui.bootstrap','ui.router', 'ngCookies','angularFileUpload']);

// regattaApp.config(['$routeProvider',
//   function($routeProvider) {
//     $routeProvider.
//     when('/home', {
//       templateUrl: '../template/home.html',
//       controller: 'HomeController',
//     }).
//     when('/login', {
//       templateUrl: '../template/login.html',
//       controller: 'LoginController'
//     }).
//     when('/register', {
//       templateUrl: '../template/register.html',
//       controller: 'RegisterController'
//     }).
//     when('/view/events', {
//       templateUrl: '../template/events.html',
//       controller: 'EventsController'
//     }).
//     when('/view/events/:event_id/flightcrews', {
//       templateUrl: '../template/flightcrew.html',
//       controller: 'FlightCrewController'
//     }).
//     when('/view/teams', {
//       templateUrl: '../template/teams.html',
//       controller: 'TeamController'
//     }).
//     when('/view/results', {
//       templateUrl: '../template/results.html',
//       controller: 'ResultsController'
//     }).
//     when('/manage/start', {
//       templateUrl: '../template/start.html',
//       controller: 'StartController'
//     }).
//     when('/manage/start/:flight', {
//       templateUrl: '../template/start_race.html',
//       controller: 'StartRaceController'
//     }).
//     when('/manage/finish', {
//      templateUrl: '../template/finish.html',
//      controller: 'FinishController'
//    }).
//         when('/manage/finish/:flight', {
//      templateUrl: '../template/finish_race.html',
//      controller: 'FinishRaceController'
//    }).

//     when('/manage/lanes', {
//      templateUrl: '../template/lane_assignment.html',
//      controller: 'LaneController'
//    }).
//     // when('/admin/load', {
//     //   templateUrl: '../template/load.html',
//     //   controller: 'LoadController'
//     // }).
//     when('/admin/upload', {
//       templateUrl: '../template/upload.html',
//       controller: 'UploadController'
//     }).
//     otherwise({
//       redirectTo: '/home'
//     });
//   }]);


regattaApp.config(['$stateProvider', '$urlRouterProvider', 'USER_ROLES',
function($stateProvider, $urlRouterProvider, USER_ROLES) {

  console.log("In state");
  // For any unmatched url, redirect to /
  $urlRouterProvider.otherwise("/");
  
  // Now set up the states
  $stateProvider
    .state('home', {
      url: "/",
      templateUrl: "../template/home.html",
      controller: 'HomeController',
      data: {
           authorizedRoles: [USER_ROLES.admin, USER_ROLES.editor, USER_ROLES.guest]
      }
    })
    .state('view_events', {
      url: "/view/events",
      templateUrl: "../template/events.html",
      controller: 'EventsController',
    })
    .state('view_teams', {
      url: '/view/teams',
      templateUrl: '../template/teams.html',
      controller: 'TeamController'
    })
    .state('login', {
      url: '/login',
      templateUrl: '../template/login.html',
      controller: 'LoginController'
    })
    .state('register', {
      url: '/register',
      templateUrl: '../template/register.html',
      controller: 'RegisterController'
    })
    .state('view_event', {
      url: '/view/events/:event_id/flightcrews',
      templateUrl: '../template/flightCrew.html',
      controller: 'FlightCrewController'
    })
    .state('view_results', {
      url: '/view/results',
      templateUrl: '../template/results.html',
      controller: 'ResultsController'
    })
    .state('manage_starts', {
      url: '/manage/start',
      templateUrl: '../template/start.html',
      controller: 'StartController',
      data: {
           authorizedRoles: [USER_ROLES.admin]
      }
    })
    .state('manage_start', {
      url: '/manage/start/:flight',
      templateUrl: '../template/start_race.html',
      controller: 'StartRaceController'
    })
    .state('manage_finishs', {
      url: '/manage/finish',
     templateUrl: '../template/finish.html',
     controller: 'FinishController'
   })
   .state('manage_finish', {
      url: '/manage/finish/:flight',
     templateUrl: '../template/finish_race.html',
     controller: 'FinishRaceController'
   })
    .state('manage_lanes', {
    url: '/manage/lanes',
     templateUrl: '../template/lane_assignment.html',
     controller: 'LaneController'
   })
  .state('admin_upload', {
    url: '/admin/upload',
      templateUrl: '../template/upload.html',
      controller: 'UploadController'
    });
}]);

regattaApp.constant('USER_ROLES', {
  all : '*',
  admin : 'admin',
  editor : 'editor',
  guest : 'guest'
}).constant('AUTH_EVENTS', {
  loginSuccess : 'auth-login-success',
  loginFailed : 'auth-login-failed',
  logoutSuccess : 'auth-logout-success',
  sessionTimeout : 'auth-session-timeout',
  notAuthenticated : 'auth-not-authenticated',
  notAuthorized : 'auth-not-authorized'
})
/* Adding the auth interceptor here, to check every $http request*/
.config(function ($httpProvider) {
  $httpProvider.interceptors.push([
    '$injector',
    function ($injector) {
      return $injector.get('AuthInterceptor');
    }
  ]);
})

regattaApp.controller('HomeController', ['$scope',
  function ($scope) {
    console.log("In home controller");
  }]);


regattaApp.controller('RegisterController', ['$http','$scope',
  function ($http,$scope) {
    var registration = this;

    $scope.onRegister = function(first,last,email,password1,password2){
      console.log("registering" + password1 + " " + password2);
      if ( password1 !== password2 ){
        $scope.registration_error = "Passwords dont match";
      }
      else {
        $http.post('/api/user', { first: first, last: last, email: email, password: password1 }).success(function(data){
          console.log('registering user');
        })
      }
    }

  }]);

