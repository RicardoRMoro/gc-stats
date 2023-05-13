from flask import Flask
from functools import wraps
from flask import session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from os import path
import os

db = SQLAlchemy()
DB_NAME = "database.db"


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'ghijklm'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.getcwd(), 'website', DB_NAME)
    db.init_app(app)

    from .views import views
    from .auth import auth
    from .graphs import graphs


    app.register_blueprint(views)
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(graphs, url_prefix='/')

    from .models import TemporaryPartidas

    with app.app_context():
        create_database(app)
        db.create_all()

    return app

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def create_database(app):
    if not path.exists('website/' + DB_NAME):
        with app.app_context():
            db.create_all()
        print('Created Database!')