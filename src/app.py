from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'movies.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

movies = SQLAlchemy(app)

ma = Marshmallow(app)


class Movie(movies.Model):
    id = movies.Column(movies.Integer, primary_key=True)
    name = movies.Column(movies.String(100))
    year = movies.Column(movies.Integer)
    description = movies.Column(movies.String(200))

    def __init__(self, name, year, description):
        self.name = name
        self.year = year
        self.description = description


class MovieSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'year', 'description')


movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)


# Posts movies into database..
@app.route('/Oscarpedia', methods=['POST'])
def add_movie():
    name = request.json['name']
    year = request.json['year']
    description = request.json['description']

    new_movie = Movie(name, year, description)

    movies.session.add(new_movie)
    movies.session.commit()

    return movie_schema.jsonify(new_movie)


# General get
@app.route('/Oscarpedia', methods=['GET'])
def get_movies():
    all_movies = Movie.query.all()
    result = movies_schema.dump(all_movies)
    return jsonify(result)


# Get by ID
@app.route('/Oscarpedia/<id>', methods=['GET'])
def get_movie(id):
    movie = Movie.query.get(id)
    return movie_schema.jsonify(movie)


# Get by Year
@app.route('/Oscarpedia/search', methods=['GET'])
def get_movies_by_search():
    result = []
    args = request.args
    for k, v in args.items():
        search_movies = Movie.query.filter(Movie.__getattribute__(Movie, k) == v).all()
        result = result + movies_schema.dump(search_movies)
    return jsonify(result)


# Modify movie entry
@app.route('/Oscarpedia/<id>', methods=['PUT'])
def update_movie(id):
    movie = Movie.query.get(id)

    name = request.json['name']
    year = request.json['year']
    description = request.json['description']

    movie.name = name
    movie.year = year
    movie.description = description

    movies.session.commit()

    return movie_schema.jsonify(movie)


# Delete by id
@app.route('/Oscarpedia/<id>', methods=['DELETE'])
def delete_movie(id):
    movie = Movie.query.get(id)
    movies.session.delete(movie)
    movies.session.commit()

    return movie_schema.jsonify(movie)


# Json return for 404 error
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


if __name__ == '__main__':
    app.run(debug=True)
