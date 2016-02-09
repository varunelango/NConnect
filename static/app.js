var myApp = angular.module("myApp", ["ngRoute"]).run(function($rootScope,$http,$location) {
  $rootScope.authenticated = false;
  $rootScope.current_user = "";

  $rootScope.logout = function(){
      $http.get("/api/logout");
      $rootScope.authenticated = false;
      $rootScope.current_user = "";
  };
  $rootScope.search = function(){
      $location.path("/search");

  }

});

myApp.config(function ($routeProvider) {
  $routeProvider
    .when("/", {
      templateUrl: "static/partials/first.html"
    })
    .when("/login", {
      templateUrl: "static/partials/login.html",
      controller: "loginController"
    })
    .when("/logout", {

    })
    .when("/home", {
      templateUrl: "static/partials/home.html",
      controller: "homeController"
    })
    .when("/register", {
      templateUrl: "static/partials/register.html",
      controller: "registerController"
    })
    .when("/profile", {
      templateUrl: "static/partials/profile.html",
      controller: "myCtrl"
    })
    .when("/newblock", {
      templateUrl: "static/partials/newblock.html",
      controller: "newblockController"
    })
    .when("/map", {
      templateUrl: "static/partials/map.html",
      controller:"mapController"
    })
    .when("/bfeed", {
      templateUrl: "static/partials/bfeed.html",
      controller: "blockController"
    })
    .when("/nfeed", {
      templateUrl: "static/partials/nfeed.html",
      controller: "neighborController"
    })
    .when("/blockreqlist", {
      templateUrl: "static/partials/blockreqlist.html",
      controller: "blockreqlistController"
    })
    .when("/affeed", {
      templateUrl: "static/partials/affeed.html",
      controller: "allfrndController"
    })
    .when("/viewprofile/:item", {
      templateUrl: "static/partials/viewprofile.html",
      controller: "viewprofileController"
    })
    .when("/mfeed", {
      templateUrl: "static/partials/mfeed.html",
      controller: "msgController"
    })
    .when("/nblist", {
      templateUrl: "static/partials/nblist.html",
      controller: "nbController"
    })
    .when("/search", {
      templateUrl: "static/partials/search.html",
      controller: "searchController"
    })
    .when("/friends", {
      templateUrl: "static/partials/friendlist.html",
      controller: "flistController"
    })
    .when("/flist", {
      templateUrl: "static/partials/flist.html",
      controller: "friendlistController"
    })
    .when("/changeblock", {
      templateUrl: "static/partials/changeblock.html",
      controller: "changeBController"
    })
    .when("/detail/:item", {
      templateUrl: "static/partials/detail.html",
      controller: "detailController"
    })
    .otherwise({redirectTo: "/"});
});
