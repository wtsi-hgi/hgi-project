# GPLv3 or later
# Copyright (c) 2015 Genome Research Limited

''' Amend response with CORS headers; use with Flask's after_request '''

from flask import request, current_app

class CORS(object):
  @staticmethod
  def allowALLTheThings(response):
    this = current_app.make_default_options_response()
    allowed = this.headers['allow']
    headers = request.headers.get('Access-Control-Request-Headers', '*')

    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', headers)
    response.headers.add('Access-Control-Allow-Methods', allowed)
    response.headers.add('Access-Control-Allow-Credentials', 'true')

    return response
