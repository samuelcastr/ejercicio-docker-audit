import logging
import os

import pymysql
from flask import Flask, jsonify, request


def get_db_connection():
    return pymysql.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        user=os.environ.get("DB_USER", "techova"),
        password=os.environ.get("DB_PASSWORD", ""),
        database=os.environ.get("DB_NAME", "techova"),
        connect_timeout=3,
        cursorclass=pymysql.cursors.DictCursor,
    )


def create_app():
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "clave-por-defecto-no-produccion"),
        TESTING=os.environ.get("FLASK_TESTING", "false").lower() == "true",
    )

    logging.basicConfig(level=logging.INFO)

    @app.get("/")
    def home():
        return jsonify(
            {
                "servicio": "API TechNova",
                "version": "2.0.0",
                "estado": "operativo",
            }
        )

    @app.get("/buscar")
    def buscar_usuario():
        usuario_id = request.args.get("id", "1")
        if not usuario_id.isdigit():
            return (
                jsonify({"error": "El parámetro 'id' debe ser un entero positivo"}),
                400,
            )

        try:
            conn = get_db_connection()
            try:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "SELECT id, nombre, email FROM usuarios WHERE id = %s",
                        (usuario_id,),
                    )
                    usuario = cursor.fetchone()
            finally:
                conn.close()

            if not usuario:
                return jsonify({"error": "Usuario no encontrado"}), 404
            return jsonify(usuario)
        except pymysql.MySQLError:
            app.logger.exception("Error de base de datos al buscar usuario")
            return jsonify({"error": "Base de datos no disponible"}), 503

    @app.get("/health")
    def health_check():
        return jsonify({"status": "ok"}), 200

    @app.errorhandler(pymysql.MySQLError)
    def handle_db_error(_error):
        return jsonify({"error": "Base de datos no disponible"}), 503

    @app.errorhandler(404)
    def not_found(_error):
        return jsonify({"error": "Recurso no encontrado"}), 404

    @app.errorhandler(500)
    def internal_error(_error):
        return jsonify({"error": "Error interno del servidor"}), 500

    return app


app = create_app()

if __name__ == "__main__":
    app.run(
        host=os.environ.get("HOST", "127.0.0.1"),
        port=int(os.environ.get("PORT", "8000")),
        debug=False,
    )