// GPLv3 or later
// Copyright (c) 2015 Genome Research Limited

// XHR request wrapper with preflight token authentication <%
var request = (function() {
  // API and token provider URLs
  var apiRoot       = 'http://dockerhost',
      tokenProvider = undefined;

  var token,
      attempts    = 0,
      maxAttempts = 3;

  // Get the bearer token <%
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
  }; // %>

  // There's no type checking here, so use this carefully <%
  var req = function(/* url, [method = 'GET', [data = undefined,]] success */) {
    var url, method = 'GET', data, success;

    // Parse arguments <%
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
    } // %>

    // AJAX wrapper <%
    $.ajax({
      url:         apiRoot + url,
      method:      method,
      data:        data,
      dataType:    'json',
      contentType: 'application/json',

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

      // Handle any authentication problems <%
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
      } // %>
    }); // %>
  }; // %>

  return req;
})(); // %>

// Common UI placeholders <%
var nb, ui;
// %>

// Generic controller constructor <%
var protoCtrl = function(url, methods) {
  var output = {};
  
  // Apply tags to templated URLs <%
  var resolveURL = function(data) {
    var tags = url.match(/:[^/]+/g) || [],
        resolved;

    tags.forEach(function(t) {
      var repl = data === null ? '' : data[t.slice(1)];
      resolved = url.replace(new RegExp(t, 'g'), repl)
    });

    return resolved;
  }; // %>

  var generic = {
    // Generic PUT method <%
    put: function(data) {
      var me = resolveURL(data);
      request(me, 'PUT', JSON.stringify(data), function() {
        location.reload();
      });
    }, // %>

    // Generic POST method <%
    post: function(data) {
      var collection  = resolveURL(null),
          subordinate = resolveURL(data);

      request(collection, 'POST', JSON.stringify(data), function() {
        location.hash = '#' + subordinate;
      });
    }, // %>

    // Generic DELETE method <%
    delete: function(data) {
      var toDelete   = resolveURL(data),
          collection = resolveURL(null);

      request(toDelete, 'DELETE', function() {
        location.hash = '#' + collection;
      })
    } // %>
  };

  methods.forEach(function(verb) {
    if (generic.hasOwnProperty(verb)) {
      output[verb] = generic[verb];
    }
  });

  return output;
}; // %>

// Controllers <%
var ctrl = {
  projects: protoCtrl('/projects/:name',  ['post']),
  project:  protoCtrl('/projects/:name',  ['put', 'delete']),
  users:    protoCtrl('/users/:username', ['post']),
  user:     protoCtrl('/users/:username', ['put', 'delete'])
}; // %>

// Generic view constructor <%
var protoView = function(nav, content) {
  var switchNavbar = function(which) {
    nb.children('li.active').toggleClass('active');
    nb.children('li[data-id=' + which + ']').toggleClass('active');
  };

  return function(data) {
    // Empty UI container and unbind all event handlers
    ui.empty();
    ui.off();
    
    // Assign model and create content
    ui.data('model', data);
    content();

    // Show data
    if (data) {
      ui.append('<h2><button class="btn btn-default btn-xs" type="button" data-toggle="collapse" data-target="#collapsedRaw">Toggle Raw Data</button></h2>');
      ui.append('<div class="collapse" id="collapsedRaw"><pre>' + JSON.stringify(data, null, 2) + '</pre></div>');
    }

    // Switch navbar
    switchNavbar(nav);
  };
}; // %>

// Views <%
var view = {
  // Navbar view <%
  navbar: function(data) {
    Object.keys(data.resources).forEach(function(rel) {
      var lcRel = rel.split(/\W/).slice(-1)[0].toLowerCase(),
          tcRel = lcRel.replace(/^./, function(l) { return l.toUpperCase(); }),
          href  = data.resources[rel].href;

      nb.append('<li data-id="' + lcRel + '"><a href="#' + href + '">' + tcRel + '</a></li>');
    });
  }, // %>

  // Landing page view <%
  home: protoView('home', function() {
    var data = ui.data('model');

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
  }), // %>

  // Project collection view <%
  projects: protoView('projects', function() {
    var data = ui.data('model');

    var list = data.map(function(proj) {
      return '<li><a href="#' + proj.link.href + '" rel="' + proj.link.rel+ '">' + proj.name + '</a></li>';
    }).sort().join('');

    ui.append('<h1>Projects</h1>');
    ui.append('<p>' + data.length + ' found:</p>');
    ui.append('<ul>' + list + '</ul>');

    // Controller <%
    ui.append(
      '<h2>Create New Project</h2>'
    + '<div class="row">'
    +   '<div class="col-lg-6">'
    +     '<div class="input-group">'
    +       '<input type="text" class="form-control" placeholder="New project name...">'
    +       '<span class="input-group-btn">'
    +         '<button class="btn btn-primary" type="button" data-action="create-project">Create</button>'
    +       '</span>'
    +     '</div>'
    +     '<small>Must start with a lowercase letter, followed by up to '
    +     '15 lowercase letters, numbers, dashes or underscores.</small>'
    +   '</div>'
    + '</div>'
    );

    ui.click(function(e) {
      var widget = $(e.target),
          action = widget.data('action');

      switch (action) {
        case 'create-project':
          var newInput = widget.parent().siblings(),
              newProj  = newInput.val();

          if (/^[a-z][a-z0-9_-]{0,15}$/.test(newProj)) {
            ctrl.projects.post({name: newProj});
          } else {
            newInput.val('');
            newInput.focus();
            newInput.parent().addClass('has-error');
          }

          break;
      }
    });
    // %>
  }), // %>

  // Project view <%
  project: protoView('projects', function() {
    var data    = ui.data('model'),
        diff    = {add:{}, del: {}},
        members = data.members.map(function(m) { return m.username; });

    var list = function(users) {
      return users.map(function(u) {
        return '<li><a href="#' + u.link.href + '" rel="' + u.link.rel + '">' + u.username + '</a></li>';
      }).join('');
    };

    ui.append('<h1>Project Profile</h1>');

    ui.append(
      '<dl>'
    +   '<dt>Name</dt><dd><a href="#' + data.self.href + '" rel="self">' + data.name + '</a></dd>'
    +   '<dt>Group ID</dt><dd>' + data.gid + '</dd>'
    + '</dl>'
    );

    // TODO Refactor
    if (data.members.length || data.owners.length) {
      ui.append('<h2>Project Membership</h2>');
    }

    if (data.members.length) {
      ui.append('<p>' + data.members.length + ' users:</p>');
      ui.append('<ul>' + list(data.members) + '</ul>');
    }

    if (data.owners.length) {
      ui.append('<p>' + data.owners.length + ' owners:</p>');
      ui.append('<ul>' + list(data.owners) + '</ul>');
    }

    // Controller <%
    ui.append(
      '<h2>Manage Project</h2>'
    + '<div class="btn-toolbar">'
    +   '<div class="btn-group">'
    +     '<button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown">'
    +       'Add User <span class="caret"></span>'
    +     '</button>'
    +     '<ul class="dropdown-menu scrollable-menu" role="menu" data-list="users"></ul>'
    +   '</div>'
    +   '<div class="btn-group">'
    +     '<button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown">'
    +       'Remove User <span class="caret"></span>'
    +     '</button>'
    +     '<ul class="dropdown-menu scrollable-menu" role="menu" data-list="kill"></ul>'
    +   '</div>'
    +   '<button type="button" class="btn btn-primary" disabled="disabled" data-action="commit-changes">'
    +     'Commit Changes'
    +   '</button>'
    +   '<button type="button" class="btn btn-danger" data-toggle="modal" data-target="#confirmDelete">'
    +     'Delete this Project'
    +   '</button>'
    + '</div>'
    + '<p><ul data-list="diff"></ul></p>'
    + '<div class="modal fade" tabindex="-1" id="confirmDelete" role="dialog">'
    +   '<div class="modal-dialog modal-sm">'
    +     '<div class="modal-content">'
    +       '<div class="modal-header"><h4 class="modal-title">L\'Appel du Vide</h4></div>'
    +       '<div class="modal-body">'
    +         'Are you sure you want to delete this project? This operation '
    +         'cannot be undone.'
    +       '</div>'
    +       '<div class="modal-footer">'
    +         '<button type="button" class="btn btn-danger" data-dismiss="modal" data-action="delete-project">'
    +           'I Regret Nothing!'
    +         '</button>'
    +       '</div>'
    +     '</div>'
    +   '</div>'
    + '</div>'
    );

    // Populate remove user dropdown
    (function() {
      var dropdown = ui.find('ul[data-list=kill]');

      dropdown.append(data.members.map(function(m, i) {
        return '<li><a data-action="delete-user" data-index="' + i + '">' + m.username + '</a></li>'
      }).join(''));
    })();

    // Populate add user dropdown
    request('/users/', function(data) {
      var dropdown = ui.find('ul[data-list=users]');

      dropdown.append(data.map(function(user) {
        return '<li><a data-action="add-user" data-user=\'' + JSON.stringify(user) + '\'>' + user.username + '</a></li>';
      }).sort().join(''));
    });

    // Update diff view
    var viewDiff = (function() {
      var $diff = ui.find('ul[data-list=diff]');

      return function() {
        var toAdd = Object.keys(diff.add),
            toDel = Object.keys(diff.del);

        var list = '';

        toDel.forEach(function(a) { list += '<li>Remove ' + a + '</li>'; });
        toAdd.forEach(function(a) { list += '<li>Add ' + a + '</li>'; });

        $diff.empty();
        $diff.append(list);
      };
    })();

    // Assign functionality to buttons <%
    ui.click(function(e) {
      var widget = $(e.target),
          action = widget.data('action');

      switch (action) {
        case 'add-user':
          var newUser = widget.data('user'),
              changed = false;

          newUser.link.rel = 'x-member';
          
          // Check for conflicts
          if (diff.del.hasOwnProperty(newUser.username)) {
            delete diff.del[newUser.username];
            changed = true;
          } else if (members.indexOf(newUser.username) == -1) {
            diff.add[newUser.username] = newUser;
            changed = true;
          }

          if (changed) {
            ui.find('button[data-action=commit-changes]').removeAttr('disabled');
            viewDiff();
          }
          break;

        case 'delete-user':
          var delUser = widget.data('index');
          diff.del[widget.text()] = delUser;

          ui.find('button[data-action=commit-changes]').removeAttr('disabled');
          viewDiff();
          break;

        case 'commit-changes':
          // Apply diff
          var toRemove = [];
          for (a in diff.del) { toRemove.push(diff.del[a]); }

          // Reverse the list, so we don't screw up indices when deleting
          toRemove.sort(function(a, b) { return b - a; })
                  .forEach(function(i) {
                    data.members.splice(i, 1);
                  });

          // Add new users
          for (a in diff.add) { data.members.push(diff.add[a]); }

          ctrl.project.put(data);
          break;

        case 'delete-project':
          ctrl.project.delete(data);
          break;
      }
    }); // %>
    // %>
  }), // %>

  // User collection view <%
  users: protoView('users', function() {
    var data = ui.data('model');

    var list = data.map(function(user) {
      return '<li><a href="#' + user.link.href + '" rel="' + user.link.rel+ '">' + user.username + '</a></li>';
    }).sort().join('');

    ui.append('<h1>Users</h1>');
    ui.append('<p>' + data.length + ' found:</p>');
    ui.append('<ul>' + list + '</ul>');
  }), // %>

  // User view <%
  user: protoView('users', function() {
    var data = ui.data('model');

    var list = function(users) {
      return users.map(function(u) {
        return '<li><a href="#' + u.link.href + '" rel="' + u.link.rel + '">' + u.name + '</a></li>';
      }).join('');
    };

    ui.append('<h1>User Profile</h1>');

    ui.append('<dl>' +
              '<dt>Username</dt><dd><a href="#' + data.self.href + '" rel="' + data.self.rel + '">' + data.username + '</a></dd>' +
              '<dt>User ID</dt><dd>' + data.uid + '</dd>' +
              '<dt>Farm User</dt><dd>' + (data.farm_user ? 'Yes' : 'No') + '</dd>' +
              '</dl>');

    // TODO Refactor
    if (data.memberof_projects.length || data.ownerof_projects.length) {
      ui.append('<h2>Project Membership</h2>');
    }

    if (data.memberof_projects.length) {
      ui.append('<p>User of ' + data.memberof_projects.length + ' projects:</p>');
      ui.append('<ul>' + list(data.memberof_projects) + '</ul>');
    }

    if (data.ownerof_projects.length) {
      ui.append('<p>Owner of ' + data.ownerof_projects.length + ' projects:</p>');
      ui.append('<ul>' + list(data.ownerof_projects) + '</ul>');
    }
  }), // %>

  // Unknown data view <%
  wtf: protoView('', function() {
    ui.append('<h1>Unknown Endpoint</h1>');
  }) // %>
}; // %>

// Routing <%
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
})(); // %>

// Let's do this! <%
$(document).ready(function() {
  nb = $('#menu'),
  ui = $('#content');

  // Populate navbar
  request('/', view.navbar);

  // Opening page
  route(location.hash || '#/');

  // Route on address change
  $(window).on('popstate', function() { route(location.hash); });
}); // %>

// vim:fdm=marker fmr=<%,%>
