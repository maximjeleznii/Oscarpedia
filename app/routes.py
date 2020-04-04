from flask import render_template, flash, redirect, jsonify, make_response, request
from app import app, db, ma
from app.models import *


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
@app.route('/Oscarpedia/json', methods=['GET'])
def get_movies_json():
    all_movies = Movie.query.all()
    results = movies_schema.dump(all_movies)
    return jsonify(results)


# General html get
@app.route('/Oscarpedia', methods=['GET'])
def get_movies():
    all_movies = Movie.query.all()
    results = movies_schema.dump(all_movies)
    return render_template('index.html', results=results)


# Get by ID
@app.route('/Oscarpedia/<id>', methods=['GET'])
def get_movie(id):
    movie = Movie.query.get(id)
    return movie_schema.jsonify(movie)


# Get by search
@app.route('/Oscarpedia/search', methods=['GET'])
def get_movies_by_search():
    result = []
    args = request.args

    #comes up with search results for every request in args
    for k, v in args.items():

        #relationship searches need their own if instances, such as oscars
        try:
            if k.lower() in "oscars":
                search_movies = Movie.query.filter(Movie.oscars.any(Oscar.category.contains(v))).all()
            else:
                search_movies = Movie.query.filter(Movie.__getattribute__(Movie, k).contains(v)).all()
        except:
            pass

        #checks if results of search are already in the result
        for movie in search_movies:

            #only adds searches not already in result
            if movie not in result:
                templist = [movie]
                result = result + templist

    return jsonify(movie_schema.dump(result, many=True))


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

