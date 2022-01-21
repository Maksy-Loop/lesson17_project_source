# app.py

from flask import Flask, request, jsonify, make_response
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
director_ns = api.namespace('directors')
genre_ns = api.namespace('genres')


@movie_ns.route("/")
class MoviesView(Resource):
    def get(self):
        page = request.args.get("page")
        director_id = request.args.get("director_id")
        genre_id = request.args.get("genre_id")
        if page:
            all_movies = db.session.query(Movie).limit(5).offset((int(page) - 1) * 5).all()
            return make_response(jsonify(movies_schema.dump(all_movies)), 200)
        elif director_id:
            movies = db.session.query(Movie).filter(Movie.director_id == int(director_id)).all()
            return make_response(jsonify(movies_schema.dump(movies)), 200)
        elif genre_id:
            movies = db.session.query(Movie).filter(Movie.genre_id == int(genre_id)).all()
            return make_response(jsonify(movies_schema.dump(movies)), 200)
        else:
            return "404", 404

    def post(self):
        data = request.json
        new_movie = Movie(**data)
        with db.session.begin():
            db.session.add(new_movie)
        return "done", 201


@movie_ns.route("/<int:id>")
class MovieView(Resource):
    def get(self, id: int):
        try:
            movie = db.session.query(Movie).filter(Movie.id == id).one()
            return jsonify(movie_schema.dump(movie))
        except Exception:
            return "404", 404

    def put(self, id: int):
        movie = db.session.query(Movie).get(id)
        data = request.json
        movie.title = data.get("title")
        movie.description = data.get("description")
        movie.trailer = data.get("trailer")
        movie.year = data.get("year")
        movie.rating = data.get("rating")
        movie.genre_id = data.get("genre_id")
        movie.director_id = data.get("director_id")
        db.session.add(movie)
        db.session.commit()
        return "", 204

    def delete(self, id: int):
        movie = db.session.query(Movie).get(id)
        db.session.delete(movie)
        db.session.commit()
        return "", 204


@director_ns.route("/")
class DirectorsView(Resource):
    def get(self):
        all_directors = db.session.query(Director).all()
        return make_response(jsonify(directors_schema.dump(all_directors)), 200)


@director_ns.route("/<int:id>")
class DirectorView(Resource):
    def get(self, id: int):
        try:
            director = db.session.query(Director).filter(Director.id == id).one()
            return jsonify(director_schema.dump(director))
        except Exception:
            return "404", 404


@genre_ns.route("/")
class GenresView(Resource):
    def get(self):
        all_genre = db.session.query(Genre).all()
        return make_response(jsonify(directors_schema.dump(all_genre)), 200)


@genre_ns.route("/<int:id>")
class GenreView(Resource):
    def get(self, id: int):
        try:
            genre = db.session.query(Genre).filter(Genre.id == id).one()
            movies = db.session.query(Movie.title).filter(Movie.genre_id == id).all()
            movies_dict = movies_schema.dump(movies)
            genre_dict = genre_schema.dump(genre)
            list_films = [title["title"] for title in movies_dict]
            genre_dict["movies"] = list_films

            return make_response(jsonify(genre_dict), 200)
        except Exception:
            return f"404", 404


if __name__ == '__main__':
    app.run(debug=True)
