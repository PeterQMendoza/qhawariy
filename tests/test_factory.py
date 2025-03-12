# import pytest

# from flask import g, session

# from qhawariy import db
from qhawariy.models.usuario import Usuario


def test_register(client, app):
    assert client.get('auth/register').status_code == 200
    response = client.post(
        '/auth/register',
        data={'email': 'peterqm@hotmail.com', 'password': '1huacachinA'}
    )
    assert response.headers['Location'] == "/auth/login"
    with app.app_context():
        assert Usuario.obtener_usuario_por_nombre("Peter") is None
