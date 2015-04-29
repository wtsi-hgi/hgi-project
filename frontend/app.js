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

// Generic view constructor
var protoview = function(nav, content) {
  return function(data) {
    // Empty UI container
    ui.empty();
    
    // Create content
    content(data);

    // Show data
    if (data) {
      ui.append('<h2><button class="btn btn-default" type="button" data-toggle="collapse" data-target="#collapsedRaw">Toggle Raw Data</button></h2>');
      ui.append('<div class="collapse" id="collapsedRaw"><pre>' + JSON.stringify(data, null, 2) + '</pre></div>');
    }

    // Switch navbar
    switchNavbar(nav);
  };
};

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
  home: protoview('home', function(data) {
    var list = Object.keys(data.resources).map(function(res) {
      return '<li><a href="#' + data.resources[res].href + '" rel="' + res + '">' + res + '</a></li>';
    }).join('');

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
  }),

  // Project collection view
  projects: protoview('projects', function(data) {
    var list = data.map(function(proj) {
      return '<li><a href="#' + proj.link.href + '" rel="' + proj.link.rel+ '">' + proj.name + '</a></li>';
    }).join('');

    ui.append('<h1>Projects</h1>');
    ui.append('<p>' + data.length + ' found</p>');
    ui.append('<ul>' + list + '</ul>');
  }),

  // Project view
  project: protoview('projects', function(data) {
    // Merge project ownership into membership
    var list = (function() {
      var ownerOf = {};

      data.owners.forEach(function(user) {
        ownerOf[user.username] = user.link.rel;
      });

      return data.members.map(function(user) {
        var rel  = [user.link.rel],
            desc = user.username;

        if (ownerOf.hasOwnProperty(user.username)) {
          rel.push(ownerOf[user.username]);
          desc += '</a> (Owner)';
        } else {
          desc += '</a>';
        }

        return '<li><a href="#' + user.link.href + '" rel="' + rel.join() + '">' + desc + '</li>';
      }).join('');
    })();

    ui.append('<h1>Project Profile</h1>');

    ui.append('<dl>' +
              '<dt>Name</dt><dd><a href="#' + data.self.href + '" rel="self">' + data.name + '</a></dd>' +
              '<dt>Group ID</dt><dd>' + data.gid + '</dd>' +
              '</dl>');

    if (data.members.length) {
      ui.append('<h2>Project Users</h2>');
      ui.append('<p>' + data.members.length + ' users:</p>');
      ui.append('<ul>' + list + '</ul>');
    }
  }),

  // User collection view
  users: protoview('users', function(data) {
    var list = data.map(function(user) {
      return '<li><a href="#' + user.link.href + '" rel="' + user.link.rel+ '">' + user.username + '</a></li>';
    }).join('');

    ui.append('<h1>Users</h1>');
    ui.append('<p>' + data.length + ' found</p>');
    ui.append('<ul>' + list + '</ul>');
  }),

  // User view
  user: protoview('users', function(data) {
    // Merge project ownership into membership
    var list = (function() {
      var ownerOf = {};

      data.ownerof_projects.forEach(function(proj) {
        ownerOf[proj.name] = proj.link.rel;
      });

      return data.memberof_projects.map(function(proj) {
        var rel  = [proj.link.rel],
            desc = proj.name;

        if (ownerOf.hasOwnProperty(proj.name)) {
          rel.push(ownerOf[proj.name]);
          desc += '</a> (Owner)';
        } else {
          desc += '</a>';
        }

        return '<li><a href="#' + proj.link.href + '" rel="' + rel.join() + '">' + desc + '</li>';
      }).join('');
    })();

    ui.append('<h1>User Profile</h1>');

    ui.append('<dl>' +
              '<dt>Username</dt><dd><a href="#' + data.self.href + '" rel="' + data.self.rel + '">' + data.username + '</a></dd>' +
              '<dt>User ID</dt><dd>' + data.uid + '</dd>' +
              '<dt>Farm User</dt><dd>' + (data.farm_user ? 'Yes' : 'No') + '</dd>' +
              '</dl>');

    if (data.memberof_projects.length) {
      ui.append('<h2>Project Membership</h2>');
      ui.append('<p>' + data.memberof_projects.length + ' projects:</p>');
      ui.append('<ul>' + list + '</ul>');
    }
  }),

  // Unknown data view
  wtf: protoview('', function(data) {
    ui.append('<h1>Unknown Endpoint</h1>');
  })
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

  // Opening page
  route(location.hash || '#/');

  // Route on address change
  $(window).on('popstate', function() { route(location.hash); });
});
