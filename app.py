# app.py

from flask import Flask, request, jsonify, abort
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_AS_ASCII'] = False


db = SQLAlchemy(app)


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")

class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class MovieSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int()
    director_id = fields.Int()


class DirectorSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


class GenreSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)

director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)

genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)


api = Api(app)



movie_ns = api.namespace('movies')
director_ns = api.namespace('director')
genre_ns = api.namespace('genres')


@movie_ns.route("/")
class MoviesView(Resource):
    def get(self):
        page = request.args.get("page")
        if page is None:
            return "404", 404
        elif page.isalpha():
            return "404", 404
        else:
            if int(page) == 1:
                all_movies = db.session.query(Movie).limit(5).all()
                movies_dict = movies_schema.dump(all_movies)
                return jsonify(movies_dict)
            elif int(page) > 1:
                all_movies = db.session.query(Movie).limit(5).offset((int(page) - 1) * 5).all()
                movies_dict = movies_schema.dump(all_movies)
                return jsonify(movies_dict)
            else:
                return "404", 404


@movie_ns.route("/<int:id>")
class MovieView(Resource):
    def get(self, id: int):
        try:
            movie = db.session.query(Movie).filter(Movie.id == id).one()
            return jsonify(movie_schema.dump(movie))
        except Exception:
            return "404", 404


@movie_ns.route("/director/")
class MoviesView(Resource):
    def get(self):
        director_id = request.args.get("director_id")
        if director_id is None:
            return "404", 404
        elif director_id.isalpha():
            return "404", 404
        else:
            movies = db.session.query(Movie).filter(Movie.director_id == int(director_id)).all()
            return jsonify(movies_schema.dump(movies))

@movie_ns.route("/genre/")
class MoviesView(Resource):
    def get(self):
        genre_id = request.args.get("genre_id")
        if genre_id is None:
            return "404", 404
        elif genre_id.isalpha():
            return "404", 404
        else:
            movies = db.session.query(Movie).filter(Movie.genre_id == int(genre_id)).all()
            return jsonify(movies_schema.dump(movies))


if __name__ == '__main__':
    app.run(debug=True)
