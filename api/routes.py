"""API RESTful de videojuegos con Flask-RESTful.

Endpoints:
    GET    /api/juegos        -> lista todos los juegos            (200)
    POST   /api/juegos        -> crea un juego                     (201, 400)
    GET    /api/juegos/<id>   -> obtiene un juego                  (200, 404)
    PUT    /api/juegos/<id>   -> modifica un juego                 (200, 400, 404)
    DELETE /api/juegos/<id>   -> elimina un juego                  (204, 404)
"""
from flask import url_for
from flask_restful import Resource, abort, fields, marshal_with, reqparse

from api import api
from models import Juego, db

# ---------------------------------------------------------------------------
# Serializacion: define como se convierte un objeto Juego a JSON
# (equivalente a to_json() del Capitulo 14, pero declarativo)
# ---------------------------------------------------------------------------
campos_juego = {
    "id": fields.Integer,
    "titulo": fields.String,
    "genero": fields.String,
    "plataforma": fields.String,
    "anio": fields.Integer(default=None),  # sin esto, un anio vacio sale como 0
    "precio": fields.Float,
    # Enlace al propio recurso (idea HATEOAS del Capitulo 14: URL completa)
    "url": fields.Url("api.juegoresource", absolute=True),
}


# ---------------------------------------------------------------------------
# Validacion de la entrada JSON (si algo falla, Flask-RESTful responde 400)
# ---------------------------------------------------------------------------
def crear_parser(requerido):
    """requerido=True para POST (campos obligatorios), False para PUT."""
    p = reqparse.RequestParser(bundle_errors=True)
    p.add_argument("titulo", type=str, required=requerido, location="json",
                   help="El titulo es obligatorio y debe ser texto")
    p.add_argument("genero", type=str, required=requerido, location="json",
                   help="El genero es obligatorio y debe ser texto")
    p.add_argument("plataforma", type=str, required=requerido, location="json",
                   help="La plataforma es obligatoria y debe ser texto")
    p.add_argument("anio", type=int, location="json",
                   help="El anio debe ser un numero entero")
    p.add_argument("precio", type=float, location="json",
                   help="El precio debe ser un numero")
    return p


def validar_texto_no_vacio(datos):
    """Rechaza cadenas vacias en los campos de texto (400 Bad Request)."""
    for campo in ("titulo", "genero", "plataforma"):
        valor = datos.get(campo)
        if valor is not None and valor.strip() == "":
            abort(400, message={campo: "No puede estar vacio"})


def obtener_juego_o_404(id):
    juego = db.session.get(Juego, id)
    if juego is None:
        abort(404, message=f"El juego con id {id} no existe")
    return juego


# ---------------------------------------------------------------------------
# Recurso coleccion: /api/juegos
# ---------------------------------------------------------------------------
class JuegoList(Resource):

    @marshal_with(campos_juego)
    def get(self):
        """GET /api/juegos -> 200 OK con la lista de juegos."""
        return Juego.query.order_by(Juego.id).all()

    @marshal_with(campos_juego)
    def post(self):
        """POST /api/juegos -> 201 Created + cabecera Location del nuevo juego."""
        datos = crear_parser(requerido=True).parse_args(strict=False)
        validar_texto_no_vacio(datos)
        juego = Juego(**datos)
        db.session.add(juego)
        db.session.commit()
        ubicacion = url_for("api.juegoresource", id=juego.id, _external=True)
        return juego, 201, {"Location": ubicacion}


# ---------------------------------------------------------------------------
# Recurso individual: /api/juegos/<id>
# ---------------------------------------------------------------------------
class JuegoResource(Resource):

    @marshal_with(campos_juego)
    def get(self, id):
        """GET /api/juegos/<id> -> 200 OK, o 404 si no existe."""
        return obtener_juego_o_404(id)

    @marshal_with(campos_juego)
    def put(self, id):
        """PUT /api/juegos/<id> -> 200 OK con el juego modificado.
        Solo se actualizan los campos enviados. 404 si no existe, 400 si hay datos invalidos."""
        juego = obtener_juego_o_404(id)
        datos = crear_parser(requerido=False).parse_args(strict=False)
        validar_texto_no_vacio(datos)
        for campo, valor in datos.items():
            if valor is not None:
                setattr(juego, campo, valor)
        db.session.commit()
        return juego

    def delete(self, id):
        """DELETE /api/juegos/<id> -> 204 No Content, o 404 si no existe."""
        juego = obtener_juego_o_404(id)
        db.session.delete(juego)
        db.session.commit()
        return "", 204


# ---------------------------------------------------------------------------
# Registro de rutas. El endpoint por defecto es el nombre de la clase en
# minusculas: 'juegolist' y 'juegoresource' (con el prefijo del blueprint: 'api.')
# ---------------------------------------------------------------------------
api.add_resource(JuegoList, "/juegos")
api.add_resource(JuegoResource, "/juegos/<int:id>")
