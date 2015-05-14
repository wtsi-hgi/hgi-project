# GPLv3 or later
# Copyright (c) 2015 Genome Research Limited

'''
A factory to create an authenticated resource subclass, of Flask's
`Resource`, which in turn authenticates all requests per the
configuration that's fed to it.

All decorators must pass `user` and `roles` values into their wrapped
functions. Moreover, they must set the `X-HGI-User` and `X-HGI-Roles`
response headers, appropriately.
'''

import sys

from flask import request
from flask.ext.restful import abort, Resource
from functools import wraps

from xiongxiong import Xiongxiong


class AuthError(Exception):
  ''' Authentication exception '''
  pass


def amendResponseHeaders(response, user, roles):
  ''' Set the X-HGI-User and X-HGI-Roles response headers '''
  body, status, headers = response

  if user:
    headers['X-HGI-User'] = user

  if roles:
    headers['X-HGI-Roles'] = ', '.join(roles)

  return body, status, headers


class authDecorators:
  ''' Authorisation decorators '''

  @staticmethod
  def none(app):
    ''' No authentication '''

    # NoOp decorator
    def decorator(f):
      @wraps(f)
      def _(*args, **kwargs):
        return f(user = None, roles = None, *args, **kwargs)
      return _

    return decorator


  @staticmethod
  def token(app):
    ''' Bearer token authentication, with basic fallback '''

    # Instantiate token decoder from configuration
    try:
      algo = app.config.get('hgi-auth-algorithm', 'sha1')
      with open(app.config['hgi-auth-key'], 'rb') as keyFile:
        xiongxiong = Xiongxiong(keyFile.read(), algo)

    except Exception as e:
      # Oh dear...
      sys.exit('Unable to instantiate authentication token decoder\n' + str(e))

    # Token authentication decorator
    def decorator(f):
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
            user  = token.data[0]
            roles = token.data[1:]

            res = f(user = user, roles = roles, *args, **kwargs)
            return amendResponseHeaders(res, user, roles)

          else:
            raise AuthError('Invalid token')

        except AuthError as e:
          # Unauthorised
          abort(401, message = 'Unauthorised: %s' % e)

      return _

    return decorator


def authFactory(app):
  '''
  Authenticated resource factory: Returns a subclass of Flask's
  `Resource` with an authentication decorator
  '''
  authMethod = app.config.get('hgi-auth-method', 'none')
  decorator = getattr(authDecorators, authMethod, authDecorators.none)

  class AuthenticatedResource(Resource):
    method_decorators = [decorator(app)]

  return AuthenticatedResource
