def test_home(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Bienenido a Qhawariy' in response.data


def test_programacion(client):
    response = client.get('/programacion')
    assert response.status_code == 200
    assert b'Programacion' in response.data
