"""
Copyright (C) 2015  Genome Research Ltd.

Author: Irina Colgiu <ic4@sanger.ac.uk>

This program is part of hgi-project

hgi-project is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.
You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.

This file has been created on Apr 20, 2015.
"""

import models as m

class UserDataAccess:

    @staticmethod
    def get_all(db):
        return db.session.query(m.User).all()

    @staticmethod
    def get_user(db, username):
        """

        :param db:
        :param username:
        :return: The user found by the username provided as param.
                None if there is no user found to match that query.
        :raises: Exception if there are more than 1 user found in the database under the given username
        """
        users = db.session.query(m.User).filter(m.User.username == username).all()
        if not users:
            return None
        nr_users_found = len(users)
        if nr_users_found > 1:
            raise Exception("More than 1 user found in the DATABASE! Quitting.")
        elif nr_users_found == 1:
            return users[0]
        return None

    @staticmethod
    def add_user(db, user):
        db.session.add(user)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            #return '', 500
            raise

    @staticmethod
    def delete_user(db, user):
        db.session.delete(user)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            raise


class ProjectDataAccess:

    @staticmethod
    def get_all(db):
        return db.session.query(m.Project).all()

    @staticmethod
    def get_project(db, name):
        projects = db.session.query(m.Project).filter(m.Project.name == name).all()
        if not projects:
            return None
        nr_projects = len(projects)
        if nr_projects > 1:
            raise Exception("More than 1 project found in the DATABASE! Quitting.")
        elif nr_projects == 1:
            return projects[0]
        return None

    @staticmethod
    def add_project(db, project):
        db.session.add(project)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            #return '', 500
            raise

    @staticmethod
    def delete_project(db, project):
        db.session.delete(project)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            raise