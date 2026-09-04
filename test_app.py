from unittest.mock import patch

import pytest
from pymysql.err import OperationalError

from app import create_app


@pytest.fixture()
def client():
    app = create_app()
    app.config.update(TESTING=True)
    return app.test_client()


def test_home(client):
    respuesta = client.get("/")
    assert respuesta.status_code == 200
    assert respuesta.get_json()["estado"] == "operativo"


def test_buscar_id_valido(client):
    datos_falsos = {"id": 2, "nombre": "Luis Gómez", "email": "luis@techova.co"}
    with patch("app.get_db_connection") as mock_conn:
        cursor = mock_conn.return_value.cursor.return_value
        cursor.__enter__.return_value = cursor
        cursor.fetchone.return_value = datos_falsos
        respuesta = client.get("/buscar?id=2")

    assert respuesta.status_code == 200
    assert respuesta.get_json() == datos_falsos
    consulta, argumentos = cursor.execute.call_args.args
    assert "%s" in consulta
    assert argumentos == ("2",)


def test_buscar_id_invalido(client):
    respuesta = client.get("/buscar?id=abc")
    assert respuesta.status_code == 400

    respuesta = client.get("/buscar?id=1 OR 1=1--")
    assert respuesta.status_code == 400

    respuesta = client.get("/buscar?id=1;DROP TABLE usuarios")
    assert respuesta.status_code == 400


def test_buscar_sin_base_de_datos(client):
    with patch(
        "app.get_db_connection", side_effect=OperationalError("Base caida")
    ):
        respuesta = client.get("/buscar?id=5")
    assert respuesta.status_code == 503
    assert respuesta.get_json()["error"] == "Base de datos no disponible"


def test_buscar_usuario_no_existente(client):
    with patch("app.get_db_connection") as mock_conn:
        cursor = mock_conn.return_value.cursor.return_value
        cursor.__enter__.return_value = cursor
        cursor.fetchone.return_value = None
        respuesta = client.get("/buscar?id=9999")
    assert respuesta.status_code == 404


def test_health_determinista(client):
    for _ in range(5):
        respuesta = client.get("/health")
        assert respuesta.status_code == 200