from flask import render_template, flash, redirect, jsonify, make_response, request
from app import app, db, ma
from app.models import *
from app.forms import SearchForm

#posts movies into database from json
@app.route('/Oscarpedia/json', methods=['POST'])
def add_movie():
    name = request.json['name']
    year = request.json['year']
    description = request.json['description']

    new_movie = Movie(name, year, description)

    movies.session.add(new_movie)
    movies.session.commit()

    return movie_schema.jsonify(new_movie)

#get home page html
@app.route('/Oscarpedia', methods=['GET', 'POST'])
def get_movies():
    results=[]
    form = SearchForm()
    args = request.args
    #if no searches return all
    if not bool(args):
        all_movies = Movie.query.all()
        results = movies_schema.dump(all_movies)
        return render_template('index.html', results=results, form=form)

    #return searches      
    else:
        search_movies=search_movies = Movie.query.filter(Movie.name.contains(request.args.get('search'))).all()
        results = movies_schema.dump(search_movies)
        return render_template('search.html', results=results, form=form)

#get json by ID
@app.route('/Oscarpedia/json/<id>', methods=['GET'])
def get_movie(id):
    movie = Movie.query.get(id)
    return movie_schema.jsonify(movie)


#get all json or by search
@app.route('/Oscarpedia/json', methods=['GET'])
def search_json():
    result = []
    args = request.args

    #if no searches return all
    if not bool(args):
        all_movies = Movie.query.all()
        results = movies_schema.dump(all_movies)
        return jsonify(results)

    #else search through database
    else:

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


#modify movie entry with json
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


#delete by id
@app.route('/Oscarpedia/<id>', methods=['DELETE'])
def delete_movie(id):
    movie = Movie.query.get(id)
    movies.session.delete(movie)
    movies.session.commit()

    return movie_schema.jsonify(movie)
