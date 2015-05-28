# GPLv3 or later
# Copyright (c) 2015 Genome Research Limited

'''
Open and parse the configuration file into the Flask app's configuration
dictionary

The configuration file is the first match from:

* ./hgi-project.cfg
* ~/.hgi-project
* /etc/hgi-project.cfg

The configuration file *must* have a `general` section, which defines
the environment and, optionally, a debugging flag. The environment name
should be reflected in subsequent sections that require configuration
(e.g., database, etc.) by dash-delimited appendage.

For example:

    [general]
    environment = live
    debug = false

    [db-live]
    uri = db://username:password@live.localhost:1234/schema

    [auth-live]
    method = token
    key = /path/to/secret.key

    [db-dev]
    uri = db://username:password@dev.localhost:1234/schema

    [auth-dev]
    method = none

Required configuration sections:

* `ldap`
* `db`
* `auth`

Options will get passed into the Flask configuration with a key mapped
from `[section]-[option]` or, where such a mapping doesn't exist, to
`hgi-[section]-[option]`. In both cases, the environment is stripped
from the section name.

So, given a mapping from `db-uri` to `SQLALCHEMY_DATABASE_URI`, the
above example will be extracted as the following:

  {
    'SQLALCHEMY_DATABASE_URI':
      'db://username:password@live.localhost:1234/schema',

    'hgi-auth-method': 'token',

    'hgi-auth-key': '/path/to/secret.key'
  }

'''

import os
import sys
import ConfigParser


# Configuration file hit list
configFiles = [
  'hgi-project.cfg',
  os.path.expanduser('~/.hgi-project'),
  '/etc/hgi-project.cfg'
]

# Configuration sections
sections = [
  'ldap',
  'db',
  'auth'
]

# Option mapping
mapping = {
  'db-uri': 'SQLALCHEMY_DATABASE_URI'
}


class EnvConfig(object):
  ''' Get the section configuration for an environment '''

  def __init__(self, config):
    self.config = config
    self.environment = config.get('general', 'environment')

  def get(self, section):
    output = {}
    fqSection = '%s-%s' % (section, self.environment)

    if self.config.has_section(fqSection):
      for o in self.config.options(fqSection):
        option = '%s-%s' % (section, o)
        appOption = mapping.get(option, 'hgi-%s' % option)
        output[appOption] = self.config.get(fqSection, o)

    return output


def importConfig(app):
  ''' Import the configuration into the Flask app '''

  # Instantiate configuration from file
  config = ConfigParser.RawConfigParser()
  config.read(configFiles)

  if config.has_option('general', 'environment'):
    environment = EnvConfig(config)

    # Set debugging mode
    if config.has_option('general', 'debug'):
      app.config['DEBUG'] = config.getboolean('general', 'debug')
    else:
      app.config['DEBUG'] = False

    # Unpack environment section config
    for s in sections:
      app.config.update(**environment.get(s))

  else:
    sys.exit('Invalid configuration')
