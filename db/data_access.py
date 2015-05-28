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

class DBOperations:

    # TODO: check what exceptions does db.session.commit raise and catch them in the calling function
    @staticmethod
    def _commit_or_rollback(db):
        try:
            db.session.commit()
        except:
            db.session.rollback()
            raise


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
            raise LookupError("User "+str(username) + " doesn't exist.")
        nr_users_found = len(users)
        if nr_users_found > 1:
            raise Exception("More than 1 user found in the DATABASE! Quitting.")
        elif nr_users_found == 1:
            return users[0]

    @staticmethod
    def save_user(db, user):
        db.session.add(user)
        DBOperations._commit_or_rollback(db)

    @staticmethod
    def delete_user(db, username):
        user = UserDataAccess.get_user(db, username)
        if not user:
            raise LookupError
        db.session.delete(user)
        DBOperations._commit_or_rollback(db)


class ProjectDataAccess:

    @staticmethod
    def get_all(db):
        return db.session.query(m.Project).all()

    @staticmethod
    def get_project(db, name):
        projects = db.session.query(m.Project).filter(m.Project.name == name).all()
        if not projects:
            raise LookupError("Project "+str(name) + " doesn't exist.")
        nr_projects = len(projects)
        if nr_projects > 1:
            raise Exception("More than 1 project found in the DATABASE! There's something wrong here..Quitting.")
        elif nr_projects == 1:
            return projects[0]


    # TODO: is this a transaction?!
    @staticmethod
    def save_project(db, project):
        db.session.add(project)
        DBOperations._commit_or_rollback(db)


    @staticmethod
    def create_and_save_project(db, name, gid, users_uids, owners_uids, sec_level="2-Standard"):
        project = m.Project(name=name, gid=gid)#, sec_level=sec_level)

        owners = [UserDataAccess.get_user(db, uid) for uid in owners_uids]
        project.owners = owners

        users = [UserDataAccess.get_user(db, uid) for uid in users_uids]
        project.users = users

        ProjectDataAccess.save_project(db, project)
        return project


    @staticmethod
    def update_project(db, name, gid, users_uids, owners_uids, sec_level="2-Standard"):
        project = ProjectDataAccess.get_project(db, name)
        #project.gid = gid
        #project.sec_level = sec_level  # For some reason it doesn't work for security level, it's the way it is declared. There's an issue open on it.

        owners = [UserDataAccess.get_user(db, uid) for uid in owners_uids]
        project.owners = owners

        users = [UserDataAccess.get_user(db, uid) for uid in users_uids]
        project.users = users

        print "PROJECT before saving to the DB: " + str(project)
        #ProjectDataAccess.save_project(db, project)
        db.session.add(project)
        DBOperations._commit_or_rollback(db)


    @staticmethod
    def delete_project(db, name):
        project = ProjectDataAccess.get_project(db, name)
        db.session.delete(project)
        DBOperations._commit_or_rollback(db)

    @staticmethod
    def add_user_to_project(db, project, user):
        project.users.append(user)
        db.session.add(project)
        DBOperations._commit_or_rollback(db)

    @staticmethod
    def remove_user_from_project(db, project, user):
        project.users.remove(user)
        db.session.add(project)
        DBOperations._commit_or_rollback(db)

    @staticmethod
    def add_owner_to_project(db, project, user):
        project.owners.append(user)
        db.session.add(project)
        DBOperations._commit_or_rollback(db)

    @staticmethod
    def remove_owner_from_project(db, project, user):
        project.owners.remove(user)
        db.session.add(project)
        DBOperations._commit_or_rollback(db)
