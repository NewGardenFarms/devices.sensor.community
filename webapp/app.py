# encoding: utf-8

"""
Copyright (c) 2018, Maintainer: David Lackovic
based on Ernesto Ruge https://github.com/ruhrmobil-E/meine-luftdaten/
All rights reserved.
Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import os

from flask import Flask, render_template

from .babel import create_module as babel_create_module
from .common.context_processor import register_context_processor
from .common.filter import register_global_filters
from .extensions import db, csrf, mail, security, migrate
from .frontend import frontend
from .models import User, Role
from .personal import personal
from .users import users

__all__ = ['launch']

DEFAULT_BLUEPRINTS = [
    frontend,
    personal,
    users,
]


def launch(config=None, app_name=None, blueprints=None):
    """Create a Flask app."""

    if blueprints is None:
        blueprints = DEFAULT_BLUEPRINTS

    app = Flask(
        app_name or 'webapp',
        static_folder='../static')

    configure_app(app, config)
    configure_hook(app)
    configure_blueprints(app, blueprints)
    configure_extensions(app)
    configure_logging(app)
    configure_filters(app)
    configure_context_processor(app)
    configure_error_handlers(app)
    babel_create_module(app)
    return app


def configure_app(app, config=None):
    """Different ways of configurations."""

    # http://flask.pocoo.org/docs/api/#configuration
    app.config.from_object('webapp.default_settings')

    if config:
        app.config.from_object(config)
        return

    # get mode from os environment
    app.config.from_pyfile('config.py', silent=True)


def configure_extensions(app):
    # flask-sqlalchemy
    db.init_app(app)

    # flask-migrate
    migrate.init_app(app, db)

    # flask-wtf
    csrf.init_app(app)

    # flask-mail
    mail.init_app(app)

    # flask-babel
    # babel.init_app(app)

    from flask_security import SQLAlchemyUserDatastore
    security.init_app(app, SQLAlchemyUserDatastore(db, User, Role))


def configure_blueprints(app, blueprints):
    for blueprint in blueprints:
        app.register_blueprint(blueprint)


def configure_filters(app):
    register_global_filters(app)


def configure_context_processor(app):
    register_context_processor(app)


def configure_logging(app):
    if not os.path.exists(app.config['LOG_DIR']):
        os.makedirs(app.config['LOG_DIR'])

    from logging import DEBUG, ERROR, handlers, Formatter
    app.logger.setLevel(DEBUG)

    info_log = os.path.join(app.config['LOG_DIR'], 'info.log')
    info_file_handler = handlers.RotatingFileHandler(info_log, maxBytes=100000, backupCount=10)
    info_file_handler.setLevel(DEBUG)
    info_file_handler.setFormatter(Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
        '[in %(pathname)s:%(lineno)d]')
    )

    exception_log = os.path.join(app.config['LOG_DIR'], 'exception.log')
    exception_log_handler = handlers.RotatingFileHandler(exception_log, maxBytes=100000, backupCount=10)
    exception_log_handler.setLevel(ERROR)
    exception_log_handler.setFormatter(Formatter(
        '%(asctime)s %(levelname)s: %(message)s ')
    )
    app.logger.addHandler(info_file_handler)
    app.logger.addHandler(exception_log_handler)


def configure_hook(app):
    @app.before_request
    def before_request():
        pass


def configure_error_handlers(app):
    # @app.errorhandler(422)
    # def semantic_error(error):
    #     # return Response.make_error_resp(msg=str(error.description), code=422)
    #     return render_template("422.html")

    @app.errorhandler(404)
    def page_not_found(error):
        # return Response.make_error_resp(msg=str(error.description), code=404)
        return render_template("404.html")

    @app.errorhandler(403)
    def page_forbidden(error):
        # return Response.make_error_resp(msg=str(error.description), code=403)
        return render_template("403.html")

    @app.errorhandler(400)
    def page_bad_request(error):
        # return Response.make_error_resp(msg=str(error.description), code=400)
        return render_template("400.html")
