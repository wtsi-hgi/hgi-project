# Copyright (c) 2014, 2015 Genome Research Ltd.
#
# Author: Joshua C. Randall <jcrandall@alum.mit.edu>
#         Christopher Harrison <ch12@sanger.ac.uk>
#
# This file is part of HGIP
#
# HGIP is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>. 
#
import ConfigParser
import os
import json
import sys
from functools import wraps

from flask import Flask, request, render_template
from flask.ext.restful import reqparse, abort, Api, Resource, fields, marshal_with
from flask.ext.sqlalchemy import SQLAlchemy
from db import models as m
from db import data_access

from xiongxiong import Xiongxiong

app = Flask(__name__)

##### DEVELOPMENT CODE: START
# CORS Allow all the things...Geez, what a PITA!
@app.after_request
def CORS(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', request.headers.get('Access-Control-Request-Headers', '*'))
  response.headers.add('Access-Control-Allow-Methods', 'HEAD, GET, POST, PUT, DELETE, OPTIONS')
  response.headers.add('Access-Control-Allow-Credentials', 'true')
  return response
##### DEVELOPMENT CODE: END

# read configuration from config file
config = ConfigParser.RawConfigParser()
config_files = config.read(['/etc/hgi-project.cfg', os.path.expanduser('~/.hgi-project'), 'hgi-project.cfg'])

# configure flask sqlalchemy
##### DEVELOPMENT CODE: START
if os.environ.get('DEV'):
  app.config['SQLALCHEMY_DATABASE_URI'] = config.get('db_dev','uri')
else:
##### DEVELOPMENT CODE: END
  app.config['SQLALCHEMY_DATABASE_URI'] = config.get('db','uri')
db = SQLAlchemy(app)

# Configure and instantiate token decoder
##### DEVELOPMENT CODE: START
if os.environ.get('DEV'):
  sys.stderr.write('Development Mode: No authentication required!\n')
else:
##### DEVELOPMENT CODE: END
  app.config['TOKEN_KEY_FILE'] = config.get('token', 'secret_key')
  if config.has_option('token', 'algorithm'):
    app.config['TOKEN_ALGORITHM'] = config.get('token', 'algorithm')
  else:
    app.config['TOKEN_ALGORITHM'] = 'sha1'

  with open(app.config['TOKEN_KEY_FILE'], 'rb') as keyFile:
    xiongxiong = Xiongxiong(keyFile.read(), app.config['TOKEN_ALGORITHM'])

# setup custom error messages
errors = {
    'NotAcceptable': {
        'message': "Your client indicated that it does not accept any of the representations we support.",
        'status': 406,
        },
}

# configure flask restful
api = Api(app, default_mediatype=None, catch_all_404s=True, errors=errors)
api.representations = {}
home_api = Api(app, default_mediatype=None, catch_all_404s=True, errors=errors)
home_api.representations = {}

# def abort_if_project_doesnt_exist(name):
#     names = [p.name for p in db.session.query(m.Project).filter(m.Project.name == name)]
#     if name not in names:
#         abort(404, message="Project {0} doesn't exist.".format(name))
#
# def abort_if_user_doesnt_exist(username):
#     usernames = [p.username for p in db.session.query(m.User).filter(m.User.username == username)]
#     print "USERNAMES RETURNED from abort_if_user_not_exist: " + str(usernames)
#     if username not in usernames:
#         abort(404, message="User {0} doesn't exist.".format(username))

# parser = reqparse.RequestParser()
# parser.add_argument('gid', type=str)


@api.representation('text/plain')
@api.representation('application/json')
@home_api.representation('text/plain')
@home_api.representation('application/json-home')
def json_rep(data, status_code, headers=None):
    resp = app.make_response((json.dumps(data), status_code, headers))
    return resp

@home_api.representation('application/xhtml+xml')
def xhtml_home_rep(data, status_code, headers=None):
    html = render_template('home.xhtml', data=data, title="API Home")
    resp = app.make_response((
            html,
            status_code,
            headers,
            ))
    return resp

@api.representation('text/html')
@api.representation('application/xhtml+xml')
def xhtml_rep(data, status_code, headers=None):
    html = render_template('data.xhtml', data=data, title="Data") # TODO it would be nice if the title was Project or User
    resp = app.make_response((
            html,
            status_code,
            headers,
            ))
    return resp


# @api.representation('application/xml')
# def xml_rep(data, status_code, headers):
#     #        resp = make_response(convert_data_to_xml(data), code)
#     pass


# def external_url_handler(error, endpoint, values):
#     "Looks up an external URL when `url_for` cannot build a URL."
#     # This is an example of hooking the build_error_handler.
#     # Here, lookup_url is some utility function you've built
#     # which looks up the endpoint in some external URL registry.
#     print "external_url_handler(error=%s, endpoint=%s, values=%s)" % (error, endpoint, values)
#     #url = lookup_url(endpoint, **values)
#     url = None
#     if url is None:
#         # External lookup did not have a URL.
#         # Re-raise the BuildError, in context of original traceback.
#         exc_type, exc_value, tb = sys.exc_info()
#         if exc_value is error:
#             raise exc_type, exc_value, tb
#         else:
#             raise error
#     # url_for will use this result, instead of raising BuildError.
#     return url
#
# app.handle_url_build_error = external_url_handler

class EnumDescription(fields.Raw):
    def output(self, key, obj):
        result = getattr(obj, key)
        # if not result:
        #     return None
        # description = result.get("description")
        # if not description:
        #     return None
        # return result.description
        return result


# class RelatedLink(fields.Raw):
#     def __init__(self, rel, **kwargs):
#         self.rel = rel
#         super(RelatedLink, self).__init__(**kwargs)

#     def output(self, key, obj):
#         value = get_value(key if self.attribute is None else self.attribute, obj)

#         return marshal({'hrefvalue, {
#                 'href': fields.String,
#                 'rel': fields.String,
#                 })

class RelatedLink(fields.Url):
    def __init__(self, endpoint, rel, **kwargs):
        self.rel = rel
        self.description = kwargs.pop("description", None)
        super(RelatedLink, self).__init__(endpoint, **kwargs)

    def output(self, key, obj):
        return {
            'rel': self.rel, 
            'href': super(RelatedLink, self).output(key, obj),
            'description': self.description or str(obj),
            }

enum_fields = {
    'name': fields.String,
    'value': fields.String,
    'description': fields.String,
}

project_core_fields = {
    'name': fields.String,
}

user_core_fields = {
    'username': fields.String,
}

project_fields = project_core_fields.copy()
project_fields.update({
        'self': RelatedLink('project', 'self'),
        'gid': fields.Integer,
        'sec_level': EnumDescription,
        'owners': fields.Nested({
                'username': fields.String,
                'link': RelatedLink('user','x-owner')
                }),
        'members': fields.Nested({
                'username': fields.String,
                'link': RelatedLink('user','x-member')
                },
                                 attribute='users', 
            ),
        'collection': RelatedLink('projectlist', 'collection', description='list of projects')
        })

# project_linked_fields = project_core_fields.copy()
# project_linked_fields.update({
#         'link': RelatedLink('project', 'x-project'),
#         })

# user_linked_fields = user_core_fields.copy()
# user_linked_fields.update({
#         'link': RelatedLink('user', 'x-member'),
#         })

user_fields = user_core_fields.copy()
user_fields.update({
        'self': RelatedLink('user', 'self'),
        'uid': fields.Integer,
        'farm_user': fields.Boolean,
        'memberof_projects': fields.Nested({
                'name': fields.String,
                'link': RelatedLink('project', 'x-member-of')
                }),
        'ownerof_projects': fields.Nested({
                'name': fields.String,
                'link': RelatedLink('project', 'x-owner-of')
                }),
        'collection': RelatedLink('userlist', 'collection', description='list of users')
        })

project_list_fields = {
    'name': fields.String,
    'link': RelatedLink('project', 'self'),
}

user_list_fields = {
    'username': fields.String,
    'link': RelatedLink('user', 'self'),
}

# Authentication exception
class AuthError(Exception):
  pass

# Token authentication decorator
##### DEVELOPMENT CODE: START
if os.environ.get('DEV'):
  def authenticateToken(f):
    @wraps(f)
    def _(*args, **kwargs):
      return f(token = None, *args, **kwargs)
    return _
else:
##### DEVELOPMENT CODE: END
  def authenticateToken(f):
    @wraps(f)
    def _(*args, **kwargs):
      try:
        try:
          # Unpack Authorization request header
          method, payload = request.headers['Authorization'].split()
          method = method.lower()
        except (KeyError, ValueError):
          raise AuthError('No valid authorisation data found')

        # Decode the authorisation payload
        if method == 'bearer':
          # Decode bearer token
          token = xiongxiong(payload)

        elif method == 'basic':
          try:
            # Decode basic auth pair
            token = xiongxiong(request.authorization.username.strip(),
                               request.authorization.password.strip())
          except AttributeError:
            raise AuthError('Invalid basic authorisation pair')

        else:
          raise AuthError('Invalid authorisation method')

        # Are we good to go?
        if token.valid:
          return f(token = token, *args, **kwargs)
        else:
          raise AuthError('Invalid token')

      except AuthError as e:
        # Unauthorised
        abort(401, message = 'Unauthorised: %s' % e)

    return _

# Subclass Resource with the authentication decorator such that it
# applies to all requests
class AuthenticatedResource(Resource):
  method_decorators = [authenticateToken]

# Project
#   show a single project item and lets you delete them
class Project(AuthenticatedResource):

    @marshal_with(project_fields)
    def get(self, name, token):
        project = data_access.ProjectDataAccess.get_project(db, name)
        if not project:
            abort(404, message="Project {0} doesn't exist.".format(name))
        return project

    def delete(self, name, token):
        try:
            data_access.ProjectDataAccess.delete_project(db, name)
        except LookupError:
            return 'The project {0} does not exist, hence cannot be deleted'.format(name), 404
        return '', 204

    def put(self, name, token): #  name, gid, sec_level, users_uids, owners_uids):
        # parsing arguments from the request:
        parser = reqparse.RequestParser()
        parser.add_argument('gid', type=int)
        parser.add_argument('sec_level', type=str, default="2-Standard")
        parser.add_argument('members', type=dict, action='append')
        parser.add_argument('owners', type=dict, action='append')
        args = parser.parse_args()
        
        # Here you assume that the gid is the only thing that can be changed...
        print "IN PUT....received data: " + str(args)
        data_access.ProjectDataAccess.update_project(db, name, args['gid'], args['members'], args['owners'])

        # project = m.Project(name=name, gid=args.get('gid'), sec_level=args.get('sec_level'))
        # print "IN PUT ---- project created: " + str(project)
        # db.session.add(project)
        # try:
        #     db.session.commit()
        # except:
        #     db.session.rollback()
        #     #return '', 500
        #     raise
        # return project, 201
        return '', 201



# ProjectList
#   shows a list of all projects, and lets you POST to add new project
class ProjectList(AuthenticatedResource):
    @marshal_with(project_list_fields)
    def get(self, token):
        return data_access.ProjectDataAccess.get_all(db)

    @marshal_with(project_fields)
    def post(self, token):
        # Getting args from the request:
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True)
        parser.add_argument('gid', type=int, required=True)
        #parser.add_argument('sec_level', type=str, default="2-Standard") => causes a problem when trying to add to DB
        parser.add_argument('owners', type=str, action='append', required=True)
        parser.add_argument('users', type=str,action='append', required=True)
        args = parser.parse_args(strict=True)

        # Adding a new project: #  name, gid, owners_uids, users_uids, sec_level="2-Standard"):
        project = data_access.ProjectDataAccess.create_and_save_project(db, args['name'], args['gid'], args['owners'], args['users'])
        return project, 201

class User(AuthenticatedResource):
    @marshal_with(user_fields)
    def get(self, username, token):
        user = data_access.UserDataAccess.get_user(db, username)
        if not user:
            abort(404, message="User {0} doesn't exist.".format(username))
        return user


    def delete(self, username):
        try:
            data_access.UserDataAccess.delete_user(db, username)
        except LookupError:
            return 'The user {0} does not exist, hence cannot be deleted'.format(username), 404
        return '', 204


    def put(self, username, token):
        parser = reqparse.RequestParser()
        parser.add_argument('uid', type=int)
        parser.add_argument('farm_user', type=bool)
        parser.add_argument('project_name', type=str, action='append')
        args = parser.parse_args(strict=True)

        user = data_access.UserDataAccess.get_user(db, username)


        # project = data_access.ProjectDataAccess.get_project(db, 'hgi')
        # user = data_access.UserDataAccess.get_user(db, 'ic4')
        # #data_access.ProjectDataAccess.remove_user_from_project(db, project, user)
        #data_access.ProjectDataAccess.remove_owner_from_project(db, project, user)
        print "IN PUT -----TESTING..........."
        #print "IN PUT on user url, data received: " + str(args)
        #abort(500, message="Put not implemented.")

class UserList(AuthenticatedResource):
    @marshal_with(user_list_fields)
    def get(self, token):
        return data_access.UserDataAccess.get_all(db)

    # TODO: here -- to be discussed. This POST assumes that a new user is always given only by username and only that.
    # TODO: This depends on whether someone can add users through this interface,
    # TODO or the users are being added in LDAP first, and hgi-project-DB is updated acordingly
    @marshal_with(user_fields)
    def post(self, token):
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, required=True)
        parser.add_argument('uid', type=int, required=True)
        parser.add_argument('farm_user', type=bool)
        args = parser.parse_args(strict=True)

        user = m.User(username=args.get('username'))
        data_access.UserDataAccess.add_user(db, user)
        return user, 201


class HomeDocument(AuthenticatedResource):
    # http://tools.ietf.org/html/draft-nottingham-json-home-03
    def get(self, token):
        data = { 
            "resources": {
                "http://hgi.sanger.ac.uk/rel/projects": {
                    "href": "/projects/"
                    },
                "http://hgi.sanger.ac.uk/rel/users": {
                    "href": "/users/"
                    },
                }
            }
        headers = {'Link': ['<%s>; rel="%s"' % (value['href'], key) for key, value in data['resources'].iteritems()]}
        return data, 200, headers

##
## Actually setup the Api resource routing here
##
## N.B. URL variables used in reverse routing must match the attribute name
## used in the actual model object returned (before marshalling).
api.add_resource(ProjectList, '/projects/')
api.add_resource(Project, '/projects/<string:name>')
api.add_resource(UserList, '/users/')
api.add_resource(User, '/users/<string:username>')

home_api.add_resource(HomeDocument, '/')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0') # default port = 5000
