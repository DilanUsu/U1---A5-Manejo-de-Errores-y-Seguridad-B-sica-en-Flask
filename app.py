
import logging
import os

from flask import Flask, abort, jsonify, render_template, request
from werkzeug.exceptions import BadRequest, HTTPException, MethodNotAllowed

from api import api_bp
from models import Juego, db

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ---------------------------------------------------------------------------
# Sentry: solo se activa si existe la variable SENTRY_DSN (ver .env.example)
# ---------------------------------------------------------------------------
SENTRY_DSN = os.environ.get("SENTRY_DSN")
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.flask import FlaskIntegration
    sentry_sdk.init(dsn=SENTRY_DSN, integrations=[FlaskIntegration()])

JUEGOS_INICIALES = [
    Juego(titulo="The Legend of Zelda: Breath of the Wild", genero="Aventura",
          plataforma="Nintendo Switch", anio=2017, precio=1299.0),
    Juego(titulo="Hollow Knight", genero="Metroidvania",
          plataforma="PC", anio=2017, precio=249.0),
    Juego(titulo="Minecraft", genero="Sandbox",
          plataforma="Multiplataforma", anio=2011, precio=599.0),
]

VISTAS_VALIDAS = ("resumen", "completa")


def configurar_logging(app):
    """Escribe los errores (nivel ERROR o mayor) en errors.log."""
    file_handler = logging.FileHandler(
        os.path.join(app.root_path, "errors.log"), encoding="utf-8")
    file_handler.setLevel(logging.ERROR)
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
    app.logger.addHandler(file_handler)


def registrar_manejadores(app):

    # -----------------------------------------------------------------------
    # Manejador generico: cualquier HTTPException en /api/* responde JSON
    # -----------------------------------------------------------------------
    @app.errorhandler(HTTPException)
    def handle_api_error(e):
        if request.path.startswith("/api/"):
            # abort() de Flask-RESTful guarda su mensaje en e.data["message"]
            description = getattr(e, "data", {}).get("message", e.description)
            response = e.get_response()
            response.data = jsonify(code=e.code, name=e.name,
                                    description=description).data
            response.content_type = "application/json"
            return response
        return e

    # -----------------------------------------------------------------------
    # Manejadores especificos con pagina HTML. Flask elige el manejador mas
    # especifico, asi que estos ganan sobre HTTPException; por eso, si la
    # ruta es de la API, delegan al manejador JSON.
    # -----------------------------------------------------------------------
    @app.errorhandler(BadRequest)
    def handle_400(e):
        if request.path.startswith("/api/"):
            return handle_api_error(e)
        return render_template("400.html", error=e), 400

    @app.errorhandler(404)
    def handle_404(e):
        if request.path.startswith("/api/"):
            return handle_api_error(e)
        return render_template("404.html", error=e), 404

    @app.errorhandler(MethodNotAllowed)
    def handle_405(e):
        if request.path.startswith("/api/"):
            return handle_api_error(e)
        return render_template("405.html", error=e), 405

    @app.errorhandler(500)
    def handle_500(e):
        # Flask ya registro el traceback en app.logger (y por lo tanto en
        # errors.log) antes de llegar aqui; al usuario no se le muestra.
        if request.path.startswith("/api/"):
            return handle_api_error(e)
        return render_template("500.html"), 500


def registrar_rutas(app):

    @app.route("/")
    def inicio():
        juegos = Juego.query.order_by(Juego.id).all()
        return render_template("lista.html", juegos=juegos)

    @app.route("/videogame/<int:id>")
    def videogame(id):
        """Detalle de un juego. Requiere ?vista=resumen|completa."""
        vista = request.args.get("vista")
        if vista is None:
            abort(400, description="Falta el parámetro obligatorio 'vista' "
                                   "(usa ?vista=resumen o ?vista=completa).")
        if vista not in VISTAS_VALIDAS:
            abort(400, description=f"El valor '{vista}' no es válido para 'vista'.")
        juego = db.session.get(Juego, id)
        if juego is None:
            abort(404, description=f"El videojuego con id {id} no existe.")
        return render_template("detalle.html", juego=juego, vista=vista)

    @app.route("/forzar-error")
    def forzar_error():
        """Provoca una excepcion no HTTP para probar el 500 y el registro."""
        return str(1 / 0)


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL", "sqlite:///videojuegos.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    app.register_blueprint(api_bp)
    configurar_logging(app)
    registrar_manejadores(app)
    registrar_rutas(app)

    with app.app_context():
        db.create_all()
        if Juego.query.count() == 0:
            db.session.add_all(JUEGOS_INICIALES)
            db.session.commit()
    return app


app = create_app()

if __name__ == "__main__":
    # Con debug=True Flask muestra su depurador en lugar de 500.html,
    # por eso aqui queda desactivado (se puede activar con FLASK_DEBUG=1).
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")
