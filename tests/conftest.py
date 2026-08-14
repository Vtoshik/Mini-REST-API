import os

# Flask-SQLAlchemy binds its engine once, when db.init_app(app) runs at
# import time in main.py — setting app.config['SQLALCHEMY_DATABASE_URI']
# later (e.g. inside a fixture) has no effect on which database gets used.
# These need to be in the environment before `main` is ever imported, which
# is why they're set here in conftest.py rather than in the fixtures.
os.environ.setdefault('DATABASE_URL', 'sqlite:///:memory:')
os.environ.setdefault('SECRET_KEY', 'test-secret')
os.environ.setdefault('JWT_SECRET_KEY', 'test-jwt-secret')
