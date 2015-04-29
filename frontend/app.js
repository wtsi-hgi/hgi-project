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

var routeFromLink = function(e) { route(e.target.hash); };

var view = {
  // Navbar view
  navbar: function(data) {
    Object.keys(data.resources).forEach(function(rel) {
      var lcRel = rel.split(/\W/).slice(-1)[0].toLowerCase(),
          tcRel = lcRel.replace(/^./, function(l) { return l.toUpperCase(); }),
          href  = data.resources[rel].href;

      nb.append('<li data-id="' + lcRel + '"><a href="#' + href + '">' + tcRel + '</a></li>');
    });
  },

  // Landing page view
  home: function(data) {
    var list = Object.keys(data.resources).map(function(res) {
      return '<li><a href="#' + data.resources[res].href + '" rel="' + res + '">' + res + '</a></li>';
    }).join('');

    ui.empty();
    ui.append('<h1>HGI Project Administration</h1>');

    ui.append('<h2>Resources</h2>');
    ui.append('<ul>' + list + '</ul>');

    ui.append('<p>Lorem ipsum dolor sit amet, consectetur adipiscing ' +
              'elit, sed do eiusmod tempor incididunt ut labore et ' +
              'dolore magna aliqua. Ut enim ad minim veniam, quis ' +
              'nostrud exercitation ullamco laboris nisi ut aliquip ' +
              'ex ea commodo consequat. Duis aute irure dolor in ' +
              'reprehenderit in voluptate velit esse cillum dolore ' +
              'eu fugiat nulla pariatur. Excepteur sint occaecat ' +
              'cupidatat non proident, sunt in culpa qui officia ' +
              'deserunt mollit anim id est laborum.</p>');

    // Route all links
    ui.find('a').click(routeFromLink);

    switchNavbar('home');
  },

  // Project collection view
  projects: function(data) {
    // TODO
    ui.empty();
    ui.append('<p>Projects</p>');
    switchNavbar('projects');
  },

  // Project view
  project: function(data) {
    // TODO
    ui.empty();
    ui.append('<p>Project</p>');
    switchNavbar('projects');
  },

  // User collection view
  users: function(data) {
    // TODO
    ui.empty();
    ui.append('<p>Users</p>');
    switchNavbar('users');
  },

  // User view
  user: function(data) {
    // TODO
    ui.empty();
    ui.append('<p>User</p>');
    switchNavbar('users');
  },

  // Unknown data view
  wtf: function(data) {
    ui.empty();
    ui.append('<h1>Unknown Endpoint</h1>');
    ui.append('<p class="lead">Returned data:</p>');
    ui.append('<pre>' + JSON.stringify(data, null, 2) + '</pre>');
    switchNavbar();
  }
};

// Routing
var route = (function() {
  // Map routes to views... Not very RESTful, but time is against us!
  var viewFrom = (function() {
    var mapping = {
      "/":               view.home,
      "/users/":         view.users,
      "/users/[^/]+":    view.user,
      "/projects/":      view.projects,
      "/projects/[^/]+": view.project,
      ".*":              view.wtf
    };

    var routes = Object.keys(mapping);

    return function(endpoint) {
      var id = routes.filter(function(r) {
        return RegExp('^' + r + '$').test(endpoint);
      })[0];

      return mapping[id];
    };
  })();

  return function(endpoint) {
    // Remove the initial # character
    endpoint = endpoint.slice(1);
    request(endpoint, viewFrom(endpoint));
  };
})();

// Let's do this!
$(document).ready(function() {
  nb = $('#menu'),
  ui = $('#content');

  // Populate navbar
  request('/', view.navbar);

  // Navbar click event
  nb.click(routeFromLink);

  // Opening page
  route(location.hash || '#/');
});
