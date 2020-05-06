from flask import render_template, flash, redirect
from flask import jsonify, make_response, request, url_for
from app import app, db, ma
from app.models import *
from app.forms import SearchForm, RatingForm
import requests, json


#posts movies into database from json and using OMDB
@app.route('/Oscarpedia/json', methods=['POST'])
def add_movie():
    omdbApi = omdb_request(request.json['name'])
    name = omdbApi['Title']
    year = omdbApi['Year']
    description = omdbApi['Plot']
    oscars = request.json['oscars']
    poster = omdbApi['Poster']
    rating = omdbApi['imdbRating']
    new_movie = Movie(name, year, description, poster, rating)
    for oscar in oscars:
        search_oscar = Oscar.query.filter(Oscar.category.contains(oscar['category'])).one()
        new_movie.oscars.append(search_oscar)
    db.session.add(new_movie)
    db.session.commit()

    return movie_schema.jsonify(new_movie)


#get home page html
@app.route('/Oscarpedia', methods=['GET', 'POST'])
def get_movies():
    result=[]
    searchform = SearchForm()
    ratingform = RatingForm()
    args = request.args.copy()

    #default page value of 1
    page = args.get('page', 1, type=int)

    #removing page from args
    if(bool(args.get('page'))):
        args.pop('page')

    #constructing querystring and saving current url
    querystring = ''
    for arg in args:
        querystring = querystring+'&'+arg+'='+args.get(arg)
    this_url = url_for('get_movies', page=page)+querystring

    #Search bar functionality
    if searchform.validate_on_submit():
        search = searchform.search.data
        search_type = searchform.search_field.data
        return redirect(url_for('get_movies')+'?'+search_type+'='+search)
    
    #Rating functionality
    if ratingform.validate_on_submit():
        movie = Movie.query.get(int(ratingform.request_id.data))
        movie.num_of_ratings = movie.num_of_ratings + 1
        movie.user_rating = (movie.user_rating*(movie.num_of_ratings-1) + int(ratingform.rating.data))/movie.num_of_ratings
        db.session.commit()
        return redirect(this_url)

    #if has no search return all
    if not bool(args):
        title = "Welcome to the Oscarpedia"
        result = query_all()

    #return query of args 
    else:
        title = "Search Results"
        result = query_args(args)

    #getting page number of last page
    lastpage = int(len(result)/app.config['MOVIES_PER_PAGE'])
    if(len(result)%app.config['MOVIES_PER_PAGE']>0):
        lastpage = lastpage+1

    #checking if the given page is more than the last page or less than 1
    if(page>lastpage):
        page = lastpage
    if(page<1):
        page = 1

    #handling urls
    json_url = url_for('get_movies_json', page=page)+querystring
    first_url = url_for('get_movies', page=1)+querystring
    last_url = url_for('get_movies', page=lastpage)+querystring
    if not page==1:
        prev_url=url_for('get_movies', page=page-1)+querystring
    else:
        prev_url=first_url
    if not page==lastpage:
        next_url=url_for('get_movies', page=page+1)+querystring
    else:
        next_url=last_url
    
    #picking out results relavent ot the page
    result = result[page*app.config['MOVIES_PER_PAGE']-app.config['MOVIES_PER_PAGE']:page*app.config['MOVIES_PER_PAGE']]

    return render_template('index.html', title=title, result=result, searchform=searchform, ratingform = ratingform, json_url=json_url,
                        page=page, prev_url=prev_url, next_url=next_url, last_url=last_url, first_url=first_url, this_url=this_url)


#get all json or by search
@app.route('/Oscarpedia/json', methods=['GET'])
def get_movies_json():
    result = []
    args = request.args.copy()

    #0 is the default page value that returns non paginated results
    page = args.get('page', 0, type=int)

    #removing page from args
    if(bool(args.get('page'))):
        args.pop('page')
    
    #if no searches return all
    if not bool(args):
        result = query_all()

    #else search through database
    else:
        result = query_args(args)

    #getting page number of last page
    lastpage = int(len(result)/app.config['MOVIES_PER_PAGE'])
    if(len(result)%app.config['MOVIES_PER_PAGE']>0):
        lastpage = lastpage+1

    #checking if the given page is more than the last page or less than 0
    if(page>lastpage):
        page = lastpage
    if(page<0):
        page = 0

    #if there is a page is not 0, paginate result
    if(page!=0):
        result = result[page*app.config['MOVIES_PER_PAGE']-5:page*app.config['MOVIES_PER_PAGE']]


    return jsonify(movie_schema.dump(result, many=True))


#get json by ID
@app.route('/Oscarpedia/json/<id>', methods=['GET'])
def get_movie(id):
    movie = Movie.query.get(id)
    return movie_schema.jsonify(movie)


#modify movie entry with json
@app.route('/Oscarpedia/json/<id>', methods=['PUT'])
def update_movie(id):
    movie = Movie.query.get(id)
    
    name = request.json['name']
    year = request.json['year']
    description = request.json['description']
    oscars = request.json['oscars']
    poster = request.json['poster']
    rating = request.json['rating']
    user_rating = request.json['user_rating']
    num_of_ratings = request.json['num_of_ratings']
    IMDB_link = request.json['IMDB_link']

    movie.name = name
    movie.year = year
    movie.description = description
    movie.oscars = []
    movie.poster = poster
    movie.rating = rating
    movie.user_rating = user_rating
    movie.num_of_ratings = num_of_ratings
    movie.IMDB_link = IMDB_link
    for oscar in oscars:
        search_oscar = Oscar.query.filter(Oscar.category.contains(oscar['category'])).one()
        movie.oscars.append(search_oscar)

    db.session.commit()

    return movie_schema.jsonify(movie)


#delete by id
@app.route('/Oscarpedia/<id>', methods=['DELETE'])
def delete_movie(id):
    movie = Movie.query.get(id)
    db.session.delete(movie)
    db.session.commit()

    return movie_schema.jsonify(movie)

#gets documentation html
@app.route('/Oscarpedia/doc', methods=['GET'])
def get_doc():
    return render_template('doc.html')


#helper method that gets OMBD data for a movie
def omdb_request(request):
    url = f"{app.config['OMDB_URL']}?apikey={app.config['API_KEY']}&t={request}"
    req = requests.get(url)

    if not req.content:
        return None
    return json.loads(req.content)


#helper method to query all movies
def query_all():
    result = []
    result = Movie.query.all()
    return result


#helper method to query results for every request in args
def query_args(args):
    result = []
    search_movies = []
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
        result = add_result(result, search_movies)

    return result


#helper method to add lists of objects together
def add_result(prev_result, new_result):
    for movie in new_result:

        #only adds searches not already in result
        if movie not in prev_result:
            templist = [movie]
            prev_result = prev_result + templist
    return prev_result