// GPLv3 or later
// Copyright (c) 2015 Genome Research Limited

// XHR request wrapper with preflight token authentication
var request = (function() {
  // API and token provider URLs
  var apiRoot       = 'http://dockerhost',
      tokenProvider = undefined;

  var token,
      attempts    = 0,
      maxAttempts = 3;

  // Get the bearer token
  var refreshToken = function(callback) {
    ++attempts;

    if (tokenProvider) {
      $.ajax({
        url:      tokenProvider,
        method:   'GET',
        dataType: 'json',

        error: function(xhr, status, err) {
          console.error('Token request failed!');
          throw err;
        },

        success: function(data) {
          token = data.accessToken;
          callback();
        }
      });
    } else {
      // Good luck with that...
      callback();
    }
  };

  // There's no type checking here, so use this carefully
  var req = function(/* url, [method = 'GET', [data = undefined,]] success */) {
    var url, method = 'GET', data, success;
    switch (arguments.length) {
      case 2:
        url     = arguments[0];
        success = arguments[1];
        break;

      case 3:
        url     = arguments[0];
        method  = arguments[1];
        success = arguments[2];
        break;

      case 4:
        url     = arguments[0];
        method  = arguments[1];
        data    = arguments[2];
        success = arguments[3];
        break;

      default:
        throw new Error('Invalid arguments');
        break;
    }

    $.ajax({
      url:      apiRoot + url,
      method:   method,
      data:     data,
      dataType: 'json',

      // Set the bearer token in the request
      headers: (function() {
        if (token) {
          return {'Authorization': 'Bearer ' + token};
        } else {
          return {};
        }
      })(),

      // It worked! Reset the token attempt count
      // (Reset here as we know it's definitely working)
      success:  function(data, status, xhr) {
        attempts = 0;
        success(data, status, xhr);
      },

      // Handle any authentication problems
      error: function(xhr, status, err) {
        if (xhr.status == 401 || xhr.status == 403) {
          if (attempts < maxAttempts) {
            // Try again
            refreshToken(function() {
              req(url, method, data, success); 
            });

          } else {
            // Too many failed attempts to get the token
            throw new Error('Could not acquire a valid bearer token!')
          }
        } else {
          // Some other error
          console.error('Request failed!')
          throw err;
        }
      }
    });
  };

  return req;
})();

// Common UI placeholders
var nb, ui;

var switchNavbar = function(which) {
  nb.children('li.active').toggleClass('active');
  nb.children('li[data-id=' + which + ']').toggleClass('active');
};

var view = {
  // Navbar view
  navbar: function(data) {
    Object.keys(data.resources).forEach(function(rel) {
      var nice = rel.replace(/(?:.*\W)?(\w)(\w*)$/, function(x, y, z) { return y.toUpperCase() + z; });
      nb.append('<li data-id="' + nice.toLowerCase() + '"><a href="#' + data.resources[rel].href + '">' + nice + '</a></li>');
    });
  },

  // Landing page view
  home: function() {
    ui.empty();
    ui.append('<h1>HGI Project Administration</h1>');
    ui.append('<p class="lead">Landing page...</h1>');
    ui.append('<p>Lorem ipsum dolor sit amet, consectetur adipiscing ' +
              'elit, sed do eiusmod tempor incididunt ut labore et ' +
              'dolore magna aliqua. Ut enim ad minim veniam, quis ' +
              'nostrud exercitation ullamco laboris nisi ut aliquip ' +
              'ex ea commodo consequat. Duis aute irure dolor in ' +
              'reprehenderit in voluptate velit esse cillum dolore ' +
              'eu fugiat nulla pariatur. Excepteur sint occaecat ' +
              'cupidatat non proident, sunt in culpa qui officia ' +
              'deserunt mollit anim id est laborum.</p>');

    switchNavbar('home');
  },

  // Project collection view
  projects: function(data) {
    // TODO
    ui.empty();
    switchNavbar('projects');
  },

  // Project view
  project: function(data) {
    // TODO
    ui.empty();
    switchNavbar('projects');
  },

  // User collection view
  users: function(data) {
    // TODO
    ui.empty();
    switchNavbar('users');
  },

  // User view
  user: function(data) {
    // TODO
    ui.empty();
    switchNavbar('users');
  }
};

// Routing and HTML5 history
// TODO

// Let's do this!
$(document).ready(function() {
  nb = $('#menu'),
  ui = $('#content');

  // Populate navbar
  request('/', view.navbar);

  // Navbar click event
  nb.click(function(e) {
    // TODO This should just wrap the routing functionality
    var id = $(e.target).parent().data('id');
    if (view.hasOwnProperty(id)) {
      view[id]();
    } else {
      view.home();
    }
  });

  // Opening page
  // TODO This should respect the URL fragment
  view.home();
});
