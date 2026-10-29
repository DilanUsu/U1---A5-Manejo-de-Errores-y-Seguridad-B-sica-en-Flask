
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Juego(db.Model):
    __tablename__ = "juegos"

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    genero = db.Column(db.String(50), nullable=False)
    plataforma = db.Column(db.String(50), nullable=False)
    anio = db.Column(db.Integer, nullable=True)
    precio = db.Column(db.Float, nullable=True)

    def __repr__(self):
        return f"<Juego {self.id} {self.titulo}>"
