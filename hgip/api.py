# Copyright (c) 2014 Genome Research Ltd.
#
# Author: Joshua C. Randall <jcrandall@alum.mit.edu>
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

from flask import Flask
from flask.ext.restful import reqparse, abort, Api, Resource, fields, marshal_with

import json

import models as m
from flask.ext.sqlalchemy import SQLAlchemy

from werkzeug.exceptions import HTTPException

app = Flask(__name__)

# read configuration from config file
config = ConfigParser.RawConfigParser()
config_files = config.read(['/etc/hgi-project.cfg', os.path.expanduser('~/.hgi-project'), 'hgi-project.cfg'])

# configure flask sqlalchemy
app.config['SQLALCHEMY_DATABASE_URI'] = config.get('db','uri')
db = SQLAlchemy(app)

# configure flask restful
api = Api(app, default_mediatype=None, catch_all_404s=True)

@app.errorhandler(HTTPException)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

def abort_if_project_doesnt_exist(project_name):
    project_names = [p.name for p in db.session.query(m.Project).filter(m.Project.name == project_name)]
    if project_name not in project_names:
        abort(404, message="Project {0} doesn't exist.".format(project_name))

def abort_if_user_doesnt_exist(username):
    usernames = [p.username for p in db.session.query(m.User).filter(m.User.username == username)]
    if username not in usernames:
        abort(404, message="User {0} doesn't exist.".format(username))

parser = reqparse.RequestParser()
parser.add_argument('gid', type=str)


#@api.representation('text/plain')
@api.representation('application/json')
def json_rep(data, status_code, headers=None):
    resp = app.make_response((json.dumps(data), status_code, headers))
    return resp
    
@api.representation('application/xhtml+xml')
def xhtml_rep(data, status_code, headers=None):
    resp = app.make_response((
            "<!DOCTYPE html>\n<html xmlns=\"http://www.w3.org/1999/xhtml\">\n\t<body>\n\t\t<pre>\n%s\n\t\t</pre>\n\t</body>\n</html>\n" % (data), 
            status_code,
            headers,
            ))
    return resp
    
# @api.representation('application/xml')
# def xml_rep(data, status_code, headers):
#     #        resp = make_response(convert_data_to_xml(data), code)
#     pass


@app.errorhandler(406)
def not_acceptable(error):
    return make_response(jsonify( {'error': 'Not Acceptable'} ), 406)

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

#class RandomNumber(fields.Raw):
#    def output(self, key, obj):
#        return random.random()

#class AlwaysFive(fields.Raw):
#    def output(self, key, obj):
#        return 5

class EnumDescription(fields.Raw):
    def output(self, key, obj):
        return getattr(obj,key).description

enum_fields = {
    'name': fields.String,
    'value': fields.String,
    'description': fields.String,
}

project_core_fields = {
    'project_name': fields.String(attribute='name'),
    'link': fields.Url('project'),
}

user_core_fields = {
    'username': fields.String,
    'link': fields.Url('user'),
}

project_fields = project_core_fields.copy()
project_fields.update({
        'gid': fields.Integer,
        'sec_level': EnumDescription,
        'owners': fields.Nested(user_core_fields),
        'users': fields.Nested(user_core_fields),
        })

user_fields = user_core_fields.copy()
user_fields.update({
        'uid': fields.Integer,
        'farm_user': fields.Boolean,
        'memberof_projects': fields.Nested(project_core_fields),
        'ownerof_projects': fields.Nested(project_core_fields),
        })

project_list_fields = {
    'project_name': fields.String(attribute='name'),
    'gid': fields.Integer,
    'sec_level': EnumDescription,
    'uri': fields.Url('project'),
}

# Project
#   show a single project item and lets you delete them
class Project(Resource):
    @marshal_with(project_fields)
    def get(self, name):
        abort_if_project_doesnt_exist(name)
        proj = db.session.query(m.Project).filter(m.Project.name == name)[0]
        return proj
        
    def delete(self, name):
        abort_if_project_doesnt_exist(name)
        abort(500, message="Delete not implemented.")
        #del db.session.query(m.Project).filter(m.Project.name == name)[0]
#        return '', 204
        
    def put(self, name):
        args = parser.parse_args()
        gid = {'gid': args['gid']}
        project = models.Project(name=name, gid=gid)
        session.add(project)
        try:
            session.commit()
        except: 
            session.rollback()
            #return '', 500
            raise
        return project, 201


# ProjectList
#   shows a list of all projects, and lets you POST to add new project
class ProjectList(Resource):
    @marshal_with(project_list_fields)
    def get(self):
        projects = db.session.query(m.Project).all()
        return projects

    def post(self):
        args = parser.parse_args()
        name = {'project_name': args['project_name']}
        project = models.Project(name=name)
        session.add(project)
        try:
            session.commit()
        except: 
            session.rollback()
            #return '', 500
            raise
        return project, 201

class User(Resource):
    @marshal_with(user_fields)
    def get(self, username):
        abort_if_user_doesnt_exist(username)
        user = db.session.query(m.User).filter(m.User.username == username)[0]
        return user
        
    def delete(self, name):
        abort_if_project_doesnt_exist(name)
        abort(500, message="Delete not implemented.")
        
    def put(self, name):
        args = parser.parse_args()
        abort(500, message="Put not implemented.")



##
## Actually setup the Api resource routing here
##
## N.B. URL variables used in reverse routing must match the attribute name 
## used in the actual model object returned (before marshalling).
api.add_resource(ProjectList, '/projects/')
api.add_resource(Project, '/projects/<string:name>')
api.add_resource(User, '/users/<string:username>')

#@app.route('/')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
