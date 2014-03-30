# Copyright (c) 2014 Genome Research Ltd.
#
# Author: Joshua C. Randall <jcrandall@alum.mit.edu>
#
# This file is part of HGIProject.
#
# HGIProject is free software: you can redistribute it and/or modify it under
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
from flask import Flask
from flask.ext.restful import reqparse, abort, Api, Resource

app = Flask(__name__)
api = Api(app)

PROJECTS = {
    'project1': {'gid': 1001},
    'project2': {'gid': 1002},
    'project3': {'gid': 1003},
}


def abort_if_project_doesnt_exist(project_id):
    if project_id not in PROJECTS:
        abort(404, message="Project {} doesn't exist".format(project_id))

parser = reqparse.RequestParser()
parser.add_argument('gid', type=str)


# Project
#   show a single project item and lets you delete them
class Project(Resource):
    def get(self, project_id):
        abort_if_project_doesnt_exist(project_id)
        return PROJECTS[project_id]

    def delete(self, project_id):
        abort_if_project_doesnt_exist(project_id)
        del PROJECTS[project_id]
        return '', 204

    def put(self, project_id):
        args = parser.parse_args()
        gid = {'gid': args['gid']}
        PROJECTS[project_id] = gid
        return gid, 201


# ProjectList
#   shows a list of all projects, and lets you POST to add new gids
class ProjectList(Resource):
    def get(self):
        return PROJECTS

    def post(self):
        args = parser.parse_args()
        project_id = 'project%d' % (len(PROJECTS) + 1)
        PROJECTS[project_id] = {'gid': args['gid']}
        return PROJECTS[project_id], 201

##
## Actually setup the Api resource routing here
##
api.add_resource(ProjectList, '/projects')
api.add_resource(Project, '/projects/<string:project_id>')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
