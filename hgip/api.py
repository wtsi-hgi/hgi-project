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

app = Flask(__name__)

# read configuration from config file
config = ConfigParser.RawConfigParser()
config_files = config.read(['hgi-project.cfg', os.path.expanduser('~/.hgi-project')])

# configure flask sqlalchemy
app.config['SQLALCHEMY_DATABASE_URI'] = config.get('db','uri')
db = SQLAlchemy(app)

# configure flask restful
api = Api(app)


def abort_if_project_doesnt_exist(project_name):
    project_names = [p.name for p in db.session.query(m.Project).filter(m.Project.name == project_name)]
    if project_name not in project_names:
        abort(404, message="Project {0} doesn't exist.".format(project_name))

parser = reqparse.RequestParser()
parser.add_argument('gid', type=str)


#@api.representation('application/json')
#@api.representation('text/plain')
#def json_rep(data, status_code, headers=None):
#    resp = api.make_response(json.dumps(data), status_code)
#    resp.headers.extend(headers or {})
#    return resp
    
# @api.representation('application/xhtml+xml')
# def xhtml_rep(data, status_code, headers):
#     #        resp = make_response(convert_data_to_xml(data), code)
#     pass
    
# @api.representation('application/xml')
# def xml_rep(data, status_code, headers):
#     #        resp = make_response(convert_data_to_xml(data), code)
#     pass


project_fields = {
    'project_name': fields.String(attribute='name'),
    'gid': fields.Integer,
    'sec_level': fields.String,
#    'uri': fields.Url('project'),
}


# Project
#   show a single project item and lets you delete them
class Project(Resource):
    @marshal_with(project_fields)

    def get(self, project_name):
        abort_if_project_doesnt_exist(project_name)
        return db.session.query(m.Project).filter(m.Project.name == project_name)[0]
        
    def delete(self, project_name):
        abort_if_project_doesnt_exist(project_name)
        abort(500, message="Delete not implemented.")
        #del db.session.query(m.Project).filter(m.Project.name == project_name)[0]
#        return '', 204
        
    def put(self, project_name):
        args = parser.parse_args()
        gid = {'gid': args['gid']}
        project = models.Project(name=project_name, gid=gid)
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
    def get(self):
        projects = db.session.query(m.Project.name).all()
        return [p.name for p in projects]

    def post(self):
        args = parser.parse_args()
        project_name = {'project_name': args['project_name']}
        project = models.Project(name=project_name)
        session.add(project)
        try:
            session.commit()
        except: 
            session.rollback()
            #return '', 500
            raise
        return project, 201

##
## Actually setup the Api resource routing here
##
api.add_resource(ProjectList, '/projects/')
api.add_resource(Project, '/projects/<string:project_name>')

#@app.route('/')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
