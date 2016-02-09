
angular.module("myApp").directive('fileModel', ['$parse', function ($parse) {
    return {
        restrict: 'A',
        link: function(scope, element, attrs) {
            var model = $parse(attrs.fileModel);
            var modelSetter = model.assign;
            
            element.bind('change', function(){
                scope.$apply(function(){
                    modelSetter(scope, element[0].files[0]);
                });
            });
        }
    };
}]);

angular.module("myApp").service('fileUpload', ['$http', function ($http) {
    this.uploadFileToUrl = function(file, uploadUrl){
        var fd = new FormData();
        fd.append('file', file);
        $http.post(uploadUrl, fd, {
            transformRequest: angular.identity,
            headers: {'Content-Type': undefined}
        })
        .success(function(){
        })
        .error(function(){
        });
    }
}]);

angular.module("myApp").controller('myCtrl', ['$scope', 'fileUpload', function($scope, fileUpload){
    
    $scope.uploadFile = function(){
        var file = $scope.myFile;
        console.log('file is ' );
        console.dir(file);
        var uploadUrl = "/import";
        fileUpload.uploadFileToUrl(file, uploadUrl);
    };   
}]);


angular.module("myApp").controller("registerController",
  ["$scope","$rootScope", "$http" ,"$location",
  function ($scope,$rootScope, $http, $location) {

      $scope.register = function() {
        var items = {"username":$scope.registerForm.username , "password":$scope.registerForm.password , "email": $scope.registerForm.email, "firstname": $scope.registerForm.firstname, "lastname": $scope.registerForm.lastname};
        console.log(items);
        $http.post("/api/register/",items)
          .success(function(data) {
            console.log(data);
            if (data.status == "Success") { 
              $location.path("/newblock"); 
              $rootScope.current_user = $scope.registerForm.username;
              console.log('Registered!');
            }
            else{
              $scope.error = true;
              $scope.errorMessage = data.message;
              $scope.registerForm = {};
            }
          })
          .error(function(data) {
            console.log("error");
            console.log(data);
        })
    };
}]);

angular.module("myApp").controller("newblockController",
  ["$scope","$rootScope", "$http" ,"$location",
  function ($scope, $rootScope, $http, $location) {
    $scope.updatenewaddress = function() {
        var items={"username":$rootScope.current_user , "doorno":$scope.address.door , "aptno": $scope.address.apt, "street": $scope.address.street, "city": $scope.address.city, "state": $scope.address.state, "zip": $scope.address.zip};
        console.log(items);
        var formData = items;
        console.log(items);
        $http.post("/api/registeraddress/",formData)
          .success(function(data) {
            console.log(data);
            if (data.status = "201") { 
            $location.path("/home"); 
            $rootScope.authenticated = true;
            console.log('import success!');
            }
          })
          .error(function(data) {
            console.log("error");
            console.log(data);
        });
    };
}]);

angular.module("myApp").controller("loginController",
  ["$scope","$http", "$rootScope", "$location",
  function ($scope, $http, $rootScope, $location) {

    $scope.login = function() {
      $scope.error = false;
      $scope.authenticated = false;
        var logindetails = {"username": $scope.loginForm.username, "password": $scope.loginForm.password};
        console.log(logindetails);
        $http.post("/api/login",logindetails)
          .success(function(data) {
            console.log(data);
            if (data.code == '200') { 
              $location.path("/home");
              $rootScope.current_user = data.user.username;
              console.log(data.user.username);
              console.log($rootScope.current_user);
              $rootScope.authenticated = true;
            }
            else{
              $scope.error = true;
              $scope.errorMessage = data.message;
              $scope.loginForm = {};
            }
          })
          .error(function(data) {
            console.log("error");
            console.log(data);
        })
    };
}]);

angular.module('appMaps', ['uiGmapgoogle-maps'])
    .controller('mainCtrl', function($scope) {
        $scope.map = {center: {latitude: 51.219053, longitude: 4.404418 }, zoom: 14 };
        $scope.options = {scrollwheel: false};
    });

angular.module("myApp").controller("mapController",
  ["$scope","$http", "$rootScope", "$location",
  function ($scope, $http, $rootScope, $location) {
    console.log("first");

    $scope.initialize = function() {
        console.log("inside init");
        var mapCanvas = document.getElementById('map');
        var mapOptions = {
          center: new google.maps.LatLng(44.5403, -78.5463),
          zoom: 8,
          mapTypeId: google.maps.MapTypeId.ROADMAP
        }
        var map = new google.maps.Map(mapCanvas, mapOptions)
      }
      google.maps.event.addDomListener(window, 'load', initialize);
}]);


angular.module("myApp").controller("logoutController",
  ["$scope","$http", "$location",
  function ($scope, $http, $location) {

    $scope.logout = function () {

      $http.get("/api/logout")
        .success(function(data){
          $location.path("/login");
        })
        .error(function(data){
          console.log("error");
          console.log(data);
        })
      
    };

}]);

angular.module("myApp").controller("blockController",
  ["$scope","$route","$http","$rootScope","$location",
  function ($scope,  $route, $http, $rootScope, $location) {
      $scope.user = $rootScope.current_user;
      $http.get("/api/blockreq/"+ $scope.user)
        .success(function(data,status){
          console.log(data);
          $scope.posts = data.items;
           console.log($scope.posts);
        })
        .error(function(data){
          console.log("error");
          console.log(data);
        })

      $scope.newposts = function() {
        console.log($scope.newPost);
        console.log($scope.newPost.text);
        var items = {"username":$rootScope.current_user, "content":$scope.newPost.text, "subject":$scope.newPost.subject, "type":"blocks"};
        console.log(items);
        var formData = items;
        console.log(items);
        $http.post("/api/post/",formData)
          .success(function(data) {
            console.log(data);
            if (data.status = "Success") { 
            $route.reload();
            console.log('import success!');
            }
          })
          .error(function(data) {
            console.log("error");
            console.log(data);
        });
    };
}]);

angular.module("myApp").controller("homeController",
  ["$scope","$route","$http","$rootScope" ,"$location",
  function ($scope,$route, $http,$rootScope, $location) {
     $scope.user = $rootScope.current_user;
     console.log($scope.user)
      $http.get("/api/hoodreq/"+ $scope.user)
        .success(function(data,status){
          console.log(data);
          $scope.posts = data.items;
           console.log($scope.posts);
        })
        .error(function(data){
          console.log("error");
          console.log(data);
        })

      $scope.newposts = function() {
        console.log($scope.newPost);
        console.log($scope.newPost.text);
        var items = {"username":$rootScope.current_user, "content":$scope.newPost.text, "subject":$scope.newPost.subject, "type":"hoods"};
        console.log(items);
        var formData = items;
        console.log(items);
        $http.post("/api/post/",formData)
          .success(function(data) {
            console.log(data);
            if (data.status = "Success") { 
            $route.reload();  
            console.log('import success!');
            }
          })
          .error(function(data) {
            console.log("error");
            console.log(data);
        });
    };
}]);

angular.module("myApp").controller("neighborController",
  ["$scope","$route","$http","$rootScope" ,"$location",
  function ($scope,$route, $http,$rootScope, $location) {
     $scope.user = $rootScope.current_user;
     console.log($scope.user)
      $http.get("/api/neigbhorreq/"+ $scope.user)
        .success(function(data,status){
          console.log(data);
          $scope.nposts = data.items;
           console.log($scope.nposts);
        })
        .error(function(data){
          console.log("error");
          console.log(data);
        })

    $scope.newposts = function() {
        console.log($scope.newPost);
        console.log($scope.newPost.text);
        var items = {"username":$rootScope.current_user, "content":$scope.newPost.text, "subject":$scope.newPost.subject, "type":"neighbours"};
        console.log(items);
        var formData = items;
        console.log(items);
        $http.post("/api/post/",formData)
          .success(function(data) {
            console.log(data);
            if (data.status = "Success") { 
            $route.reload();
            $scope.newPost = {};
            console.log('import success!');
            }
          })
          .error(function(data) {
            console.log("error");
            console.log(data);
        });
    };
}]);

angular.module("myApp").controller("allfrndController",
  ["$scope","$route","$http","$rootScope" ,"$location",
  function ($scope,$route, $http,$rootScope, $location) {
     $scope.user = $rootScope.current_user;
     console.log($scope.user)
      $http.get("/api/friendreq/"+ $scope.user)
        .success(function(data,status){
          console.log(data);
          $scope.fposts = data.items;
           console.log($scope.fposts);
        })
        .error(function(data){
          console.log("error");
          console.log(data);
        })

    $scope.newposts = function() {
        console.log($scope.newPost);
        console.log($scope.newPost.text);
        var items = {"username":$rootScope.current_user, "content":$scope.newPost.text, "subject":$scope.newPost.subject, "type":"allfriends"};
        console.log(items);
        var formData = items;
        console.log(items);
        $http.post("/api/post/",formData)
          .success(function(data) {
            console.log(data);
            if (data.status = "Success") { 
            $route.reload();  
            console.log('import success!');
            }
          })
          .error(function(data) {
            console.log("error");
            console.log(data);
        });
    };
}]);

angular.module("myApp").controller("msgController",
  ["$scope","$route","$http","$rootScope" ,"$location",
  function ($scope,$route, $http,$rootScope, $location) {
     $scope.user = $rootScope.current_user;
     console.log($scope.user)
      $http.get("/api/private/"+ $scope.user)
        .success(function(data,status){
          console.log(data);
          $scope.mposts = data.items;
        })
        .error(function(data){
          console.log("error");
          console.log(data);
        })
      console.log("msg");

    $scope.newposts = function() {
        console.log($scope.newPost);
        console.log($scope.newPost.text);
        var items = {"username":$rootScope.current_user, "content":$scope.newPost.text, "subject":$scope.newPost.subject, "type":"blocks"};
        console.log(items);
        var formData = items;
        console.log(items);
        $http.post("/api/post/",formData)
          .success(function(data) {
            console.log(data);
            if (data.status = "Success") { 
              $route.reload();  
              console.log('import success!');
            }
          })
          .error(function(data) {
            console.log("error");
            console.log(data);
        });
    };
        
}]);

angular.module("myApp").controller("profileController",
  ["$scope","$http", "$rootScope", "$location",
  function ($scope, $http, $rootScope, $location) {
    $scope.profiles = [
      { name: "Varun Elango",description :"John", interest: "Tennis",  dob :"25", imageUrl:"./static/img/Dp_Pic.jpg"}
    ];

        $scope.uploadfile = function() {
     var f = document.getElementById('file').files[0]; 

     console.log(f);
     var formData = new FormData();
     formData.append('file', f);
     console.log("FORM DATA:");
     console.log(formData);
                        $http({method: 'POST', url: '/import',
                         data: formData,
                         headers: {'Content-Type': undefined},
                         transformRequest: angular.identity})
                        .success(function(data, status, headers, config) {console.log(data);
                        if (data.success) {
                            console.log('import success!');

                        }
                    })
                    .error(function(data, status, headers, config) {
                    });
            // }
        };
}

]);

angular.module("myApp").controller("flistController",
  ["$scope","$route","$http", "$rootScope", "$location",
  function ($scope,$route, $http, $rootScope, $location) {
    console.log("friendcontrol block");
    $http.get("/api/pending/"+ $rootScope.current_user)
        .success(function(data){
          $scope.friends = data.pending;
          $scope.requested = data.requested;
          $scope.newlist = data.tobesent;
          console.log($scope.friends);
        })
        .error(function(data){
          console.log("error");
          console.log(data);
        })


    $scope.frequest = function($id) {
        var items = {username: $rootScope.current_user, toid: $id};
        console.log(items);
        $http.post("/api/friendrequest/",items)
          .success(function(data) {
            console.log(data);
            if (data.status = "Success") { 
              $route.reload();  
              console.log('requested!');
            }
          })
          .error(function(data) {
            console.log("error");
            console.log(data);
        });
    };

    $scope.approve = function($id) {
        console.log($id);
        $http.get("/api/approvefriend/"+$rootScope.current_user+"/"+$id)
          .success(function(data) {
            console.log(data);
            if (data.status = "Success") { 
              $route.reload();  
              console.log('request approved!');
            }
          })
          .error(function(data) {
            console.log("error");
            console.log(data);
        });
    };

    $scope.reject = function($id) {
        console.log($id);
        $http.get("/api/rejectfriend/"+$rootScope.current_user+"/"+$id)
          .success(function(data) {
            console.log(data);
            if (data.status = "Success") { 
              $route.reload();  
              console.log('request rejected!');
            }
          })
          .error(function(data) {
            console.log("error");
            console.log(data);
        });
    };      
}]);

angular.module("myApp").controller("friendlistController",
  ["$scope","$http", "$rootScope", "$location",
  function ($scope, $http, $rootScope, $location) {
    console.log("friendcontrol block");
    $http.get("/api/oldfriends/"+ $rootScope.current_user)
        .success(function(data){
          $scope.friends = data.items;
        })
        .error(function(data){
          console.log("error");
          console.log(data);
        })

}]);

angular.module("myApp").controller("viewprofileController",
  ["$scope","$http", "$rootScope", "$routeParams","$location",
  function ($scope, $http, $rootScope, $routeParams, $location) {
    console.log("viewprofile block");
    var currentid = $routeParams.item;
    $scope.profiles = [
      { name: "Varun Elango",description :"John", interest: "Tennis",  dob :"25" , imageUrl:"./static/img/Dp_Pic.jpg"}
    ];

    $scope.uploadfile = function(){
      $http.post('upload.ashx',$scope.files)
      .success(function(data){
        console.log('uploaded');
      })
      .error(function(data){
        console.log("error");
      })
    };
}]);

angular.module("myApp").controller("changeBController",
  ["$scope","$http", "$rootScope", "$location",
  function ($scope, $http, $rootScope, $location) {
    console.log("changeblock block");
      $scope.updateaddress = function() {
        var items={"username":$rootScope.current_user , "doorno":$scope.address.door , "aptno": $scope.address.apt, "street": $scope.address.street, "city": $scope.address.city, "state": $scope.address.state, "zip": $scope.address.zip};
        console.log(items);
        $http.post("/api/blockchange/",items)
          .success(function(data) {
            console.log(data);
            if (data.status = "Success") { 
              $location.path("/home"); 
              console.log('block request sent!');
            }
          })
          .error(function(data) {
            console.log("error");
            console.log(data);
        });
    }; 
}]);

angular.module("myApp").controller("searchController",
  ["$scope","$http", "$rootScope", "$location",
  function ($scope, $http, $rootScope, $location) {
    console.log("search block");
      $scope.user = $rootScope.current_user;
      console.log($scope.searchtext);
      $http.get("/api/search/"+ $scope.user+"/"+$scope.searchtext)
        .success(function(data,status){
          console.log(data);
          $scope.posts = data.items;
           console.log($scope.posts);
        })
        .error(function(data){
          console.log("error");
          console.log(data);
        })
}]);

angular.module("myApp").controller("detailController",
  ["$scope","$route","$http", "$rootScope", "$routeParams","$location",
  function ($scope, $route, $http, $rootScope, $routeParams, $location) {
    console.log("detail block");
      var currentid = $routeParams.item;
      $scope.comments = {}
      $http.get("/api/comments/"+ currentid)
        .success(function(data,status){
            console.log(data);
            $scope.comments = data.items;
            $scope.posts = data.post;
             console.log($scope.posts);
             console.log($scope.comments);
        })
        .error(function(data){
          console.log("error");
          console.log(data);
        })

      $scope.addcmt = function() {
        var currentid = $routeParams.item;
        var items = {"username":$rootScope.current_user , "content":$scope.newcmt , "pid": currentid}
        console.log(items);
        $http.post("/api/addcomment/",items)
          .success(function(data) {
            console.log(data);
            if (data.status = "Success") { 
              $route.reload();  
              console.log('request rejected!');
            }
          })
          .error(function(data) {
            console.log("error");
            console.log(data);
        });
    }; 
}]);

angular.module("myApp").controller("nbController",
  ["$scope","$route","$http", "$rootScope", "$location",
  function ($scope,$route, $http, $rootScope, $location) {
    console.log("NB block");
      $http.get("/api/listofneighbors/"+ $rootScope.current_user)
        .success(function(data){
            console.log(data);
            $scope.nb = data.items;
        })
        .error(function(data){
          console.log("error");
          console.log(data);
        })

      $http.get("/api/addednb/"+ $rootScope.current_user)
        .success(function(data){
            console.log(data);
            $scope.nbs = data.items;
        })
        .error(function(data){
          console.log("error");
          console.log(data);
        })

     $scope.addnb = function($id) {
        var items = {"username":$rootScope.current_user , "nid": $id}
        console.log(items);
        $http.post("/api/addnewnb/",items)
          .success(function(data) {
            console.log(data);
            if (data.status = "Success") { 
              $route.reload();  
              console.log('NB added!');
            }
          })
          .error(function(data) {
            console.log("error");
            console.log(data);
        });
    }; 

}]);

angular.module("myApp").controller("blockreqlistController",
  ["$scope","$route","$rootScope", "$http" ,"$location",
  function ($scope,$route,$rootScope, $http, $location) {

      $http.get("/api/pendingbrequest/"+ $rootScope.current_user)
        .success(function(data){
            console.log(data);
            $scope.ppls = data.items;
            console.log(data.items);
        })
        .error(function(data){
          console.log("error");
          console.log(data);
        })

      $scope.approvereq = function($id){
      console.log($id);
      $http.get("/api/acceptbrequest/"+ $scope.current_user+"/"+$id)
        .success(function(data){
          $route.reload();
          console.log("approved request");
        })
        .error(function(data){
          console.log("error");
          console.log(data);
        })
      };
}]);
