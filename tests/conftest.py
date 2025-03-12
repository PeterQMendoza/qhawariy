# import os
# import tempfile

import pytest

from qhawariy import create_app, db
from qhawariy.models.usuario import Usuario


@pytest.fixture
def app():
    app = create_app(test_config='TESTING')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


@pytest.fixture
def init_database():
    db.create_all()
    user = Usuario(
        'testerNombres',
        'testerApellidos',
        '1234567',
        '7654321',
        'tester@gmail.com'
    )
    db.session.add(user)
    db.session.commit()
    yield db
    db.drop_all()


# Authencitation of user
class AuthAction(object):
    def __init__(self, client):
        self._client = client

    def login(self, email='peterqm@hotmail.com', password='1huacachinA'):
        return self._client.post(
            '/auth/login',
            data={'username': email, 'password': password}
        )

    def logout(self):
        return self._client.get('/auth/logout')


@pytest.fixture
def auth(client):
    return AuthAction(client)
