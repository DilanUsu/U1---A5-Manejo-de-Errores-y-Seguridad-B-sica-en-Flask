from flask import Blueprint
from flask_restful import Api

# Blueprint con prefijo /api  ->  todas las rutas quedan como /api/...
api_bp = Blueprint("api", __name__, url_prefix="/api")


class ApiConManejadoresFlask(Api):
    """Flask-RESTful normalmente responde sus propios errores ({"message": ...}).
    Al relanzarlos, Flask usa los manejadores de app.py y toda la API responde
    con el mismo formato JSON: {code, name, description}."""

    def handle_error(self, e):
        raise e


api = ApiConManejadoresFlask(api_bp)

# Importar routes al final para evitar importaciones circulares
from api import routes  # noqa: E402,F401
