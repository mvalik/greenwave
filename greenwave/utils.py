# SPDX-License-Identifier: GPL-2.0+

import functools
import logging
import os
import time
import hashlib

from flask import jsonify, current_app, request
from flask.config import Config
from requests import ConnectionError, Timeout
from werkzeug.exceptions import HTTPException

log = logging.getLogger(__name__)


def json_error(error):
    """
    Return error responses in JSON.

    :param error: One of Exceptions. It could be HTTPException, ConnectionError, or
    Timeout.
    :return: JSON error response.

    """
    if isinstance(error, HTTPException):
        msg = error.description
        status_code = error.code
    elif isinstance(error, ConnectionError):
        current_app.logger.exception('Connection error: {}'.format(error))
        msg = 'Error connecting to upstream server: {}'.format(error)
        status_code = 502
    elif isinstance(error, Timeout):
        current_app.logger.exception('Timeout error: {}'.format(error))
        msg = 'Timeout connecting to upstream server: {}'.format(error)
        status_code = 504
    else:
        current_app.logger.exception('Unexpected server error: {}'.format(error))
        msg = 'Server encountered unexpected error'
        status_code = 500

    response = jsonify(message=msg)
    response.status_code = status_code

    response = insert_headers(response)

    return response


def jsonp(func):
    """Wraps Jsonified output for JSONP requests."""
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        callback = request.args.get('callback', False)
        if callback:
            resp = func(*args, **kwargs)
            resp.set_data('{}({});'.format(
                str(callback),
                resp.get_data().decode('utf-8')
            ))
            resp.mimetype = 'application/javascript'
            return resp
        else:
            return func(*args, **kwargs)
    return wrapped


def load_config(config_obj=None):
    """
    Load Greenwave configuration. It will load the configuration based on how the environment is
    configured.
    :return: A dict of Greenwave configuration.
    """
    # Load default config, then override that with a config file
    config = Config(__name__)
    if config_obj is None:
        if os.getenv('TEST') == 'true':
            config_obj = 'greenwave.config.TestingConfig'
        elif os.getenv('DEV') == 'true':
            config_obj = 'greenwave.config.DevelopmentConfig'
        else:
            config_obj = 'greenwave.config.ProductionConfig'

    if os.getenv('TEST') == 'true':
        default_config_file = os.getcwd() + '/conf/settings.py.example'
    elif os.getenv('DEV') == 'true':
        default_config_file = os.getcwd() + '/conf/settings.py'
    else:
        default_config_file = '/etc/greenwave/settings.py'

    log.debug("config: Loading config from %r", config_obj)
    config.from_object(config_obj)

    config_file = os.environ.get('GREENWAVE_CONFIG', default_config_file)
    log.debug("config: Extending config with %r", config_file)
    config.from_pyfile(config_file)

    if os.environ.get('SECRET_KEY'):
        config['SECRET_KEY'] = os.environ['SECRET_KEY']

    return config


def insert_headers(response):
    """ Insert the CORS headers for the give reponse if there are any
    configured for the application.
    """
    if current_app.config.get('CORS_URL'):
        response.headers['Access-Control-Allow-Origin'] = \
            current_app.config['CORS_URL']
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        response.headers['Access-Control-Allow-Method'] = 'POST, OPTIONS'
    return response


def retry(timeout=None, interval=None, wait_on=Exception):
    """ A decorator that allows to retry a section of code...
    ...until success or timeout.

    If omitted, the values for `timeout` and `interval` are
    taken from the global configuration.
    """
    def wrapper(function):
        @functools.wraps(function)
        def inner(*args, **kwargs):
            _timeout = timeout or current_app.config['RETRY_TIMEOUT']
            _interval = interval or current_app.config['RETRY_INTERVAL']
            # These can be configured per-function, or globally if omitted.
            start = time.time()
            while True:
                try:
                    return function(*args, **kwargs)
                except wait_on as e:  # pylint: disable=broad-except
                    log.warning("Exception %r raised from %r.  Retry in %rs",
                                e, function, _interval)
                    time.sleep(_interval)
                    if (time.time() - start) >= _timeout:
                        raise  # This re-raises the last exception.
        return inner
    return wrapper


def sha1_mangle_key(key):
    """
    Like dogpile.cache.util.sha1_mangle_key, but works correctly on
    Python 3 with str keys (which must be encoded to bytes before passing them
    to hashlib.sha1()).
    """
    return hashlib.sha1(key.encode('utf-8')).hexdigest()
