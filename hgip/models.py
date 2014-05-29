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
import sqlalchemy as sa
import decl_enum as de
from sqlalchemy_continuum import make_versioned
from sqlalchemy.ext.declarative import declared_attr, declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Sequence

if sa.__version__ < '0.6.5':
    raise NotImplementedError("SQLAlchemy version must be >= 0.6.5 for Enum support.")

# Init sqlalchemy_continuum for automatic _history table support
make_versioned(user_cls=None)


# Custom SQLAlchemy Base class
class Base(object):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    __table_args__ = {'mysql_engine': 'InnoDB'}

Base = declarative_base(cls=Base)

# Application-specific types
class DataSecurityLevel(de.DeclEnum):
    one = "1-OPEN", "1-Open"
    two = "2-STANDARD", "2-Standard"
    three = "3-STRONG", "3-Strong"
    four = "4-PERSONAL", "4-Personal"

class PrelimPrefixType(de.DeclEnum):
    g = "G", "G-General Externally Funded"
    i = "I", "I-Internally Funded"
    c = "C", "C-Cytometry Core Facility"

# Unmapped tables for many-to-many relationships
project_user_members = sa.Table('project_user_members', Base.metadata, 
                                sa.Column('project_id', sa.Integer, sa.ForeignKey('project.id'), primary_key=True),
                                sa.Column('member_user_id', sa.Integer, sa.ForeignKey('user.id'), primary_key=True),
                            )

project_user_owners = sa.Table('project_user_owners', Base.metadata, 
                               sa.Column('project_id', sa.Integer, sa.ForeignKey('project.id'), primary_key=True),
                               sa.Column('owner_user_id', sa.Integer, sa.ForeignKey('user.id'), primary_key=True),
                           )

prelim_user_pis = sa.Table('prelim_user_pis', Base.metadata, 
                           sa.Column('prelim_id', sa.Integer, sa.ForeignKey('prelim.id'), primary_key=True),
                           sa.Column('pi_user_id', sa.Integer, sa.ForeignKey('user.id'), primary_key=True),
                       )


# Application data models
class Project(Base):
    __versioned__ = {}

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(16), unique=True, index=True)
    gid = sa.Column(sa.Integer, unique=True, index=True, nullable=True)
    sec_level = sa.Column(DataSecurityLevel.db_type(), nullable=True)

    # many-to-many
    users = relationship('User', secondary=project_user_members, backref='memberof_projects')
    owners = relationship('User', secondary=project_user_owners, backref='ownerof_projects')

    def __repr__(self):
        return "<Project(name='%s', gid='%s', sec_level='%s')>" % (self.name, self.gid, self.sec_level)

    

class Prelim(Base):
    __versioned__ = {}

    id = sa.Column(sa.Integer, primary_key=True)
    prefix = sa.Column(PrelimPrefixType.db_type())
    
    # many-to-many
    pis = relationship('User', secondary=prelim_user_pis, backref='pi_of_prelims')

class User(Base):
    __versioned__ = {}

    id = sa.Column(sa.Integer, primary_key=True)
    username = sa.Column(sa.String(16), unique=True, index=True)
    uid = sa.Column(sa.Integer, unique=True, index=True)
    farm_user = sa.Column(sa.Boolean())

    def __repr__(self):
        return "<User(username='%s', uid='%s', farm_user='%s')>" % (self.username, self.uid, self.farm_user)


# Configure SQLAlchemy ORM based on models
sa.orm.configure_mappers()


#from sqlalchemy_continuum import history_class, parent_class
#history_class(Article)  # ArticleHistory class
#parent_class(history_class(Article))  # Article class
