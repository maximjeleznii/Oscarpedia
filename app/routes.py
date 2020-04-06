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
    result=[]
    form = SearchForm()
    args = request.args
    #if no searches return all
    if not bool(args):
        result = query_all()
        return render_template('index.html', result=result, form=form)

    #return searches      
    else:
        result = query_search(args.get('search'))
        return render_template('search.html', result=result, form=form)

#get all json or by search
@app.route('/Oscarpedia/json', methods=['GET'])
def search_json():
    result = []
    args = request.args
    search_movies = []

    #if no searches return all
    if not bool(args):
        result = query_all()
        return jsonify(result)

    #else search through database
    else:

        #comes up with search results for every request in args
        for k, v in args.items():

            #relationship searches need their own if instances, such as oscars
            try:
                if k.lower() in "oscars":
                    search_movies = Movie.query.filter(Movie.oscars.any(Oscar.category.contains(v))).all()
                elif k.lower() in "search":
                    search_movies = query_search(v)
                else:
                    search_movies = Movie.query.filter(Movie.__getattribute__(Movie, k).contains(v)).all()
            except:
                pass

        result = add_result(result, search_movies)

    return jsonify(movie_schema.dump(result, many=True))

#helper method to query all movies
def query_all():
    result = []
    all_movies = Movie.query.all()
    result = movies_schema.dump(all_movies)
    return result

#helper method to query by search
def query_search(query):
    result = []
    columnsList = list(movies_schema.fields.keys())
    columnsList.remove('id')
    columnsList.remove('poster')

    #looks through every column for the query
    for column in columnsList:
        if column.lower() in "oscars":
            search_movies = Movie.query.filter(Movie.oscars.any(Oscar.category.contains(query))).all()
        else:
            search_movies = Movie.query.filter(Movie.__getattribute__(Movie, column).contains(query)).all()
        print(column)
        print(search_movies)

        result = add_result(result, search_movies)

    return result

def add_result(prev_result, new_result):
    for movie in new_result:

        #only adds searches not already in result
        if movie not in prev_result:
            templist = [movie]
            prev_result = prev_result + templist
    return prev_result
    

#get json by ID
@app.route('/Oscarpedia/json/<id>', methods=['GET'])
def get_movie(id):
    movie = Movie.query.get(id)
    return movie_schema.jsonify(movie)

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

