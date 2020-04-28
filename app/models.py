from app import db, ma


#Oscar and Movie relationship table
movieOscars =  db.Table('movieOscar',
    db.Column('oscar_id', db.Integer, db.ForeignKey('oscar.id'), primary_key=True),
    db.Column('movie_id', db.Integer, db.ForeignKey('movie.id'), primary_key=True)
)


#Movie Model
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    year = db.Column(db.Integer)
    description = db.Column(db.String(200))
    oscars = db.relationship('Oscar', secondary=movieOscars, backref=db.backref('movies'))
    poster = db.Column(db.String(100))
    rating = db.Column(db.String(100))
    user_rating =  db.Column(db.Integer, )
    num_of_ratings = db.Column(db.Integer)
    IMDB_link = db.Column(db.String(200))

    def __init__(self, name, year, description, poster, rating):
        self.name = name
        self.year = year
        self.description = description
        self.poster = poster
        self.rating = rating
        self.user_rating = 0
        self.num_of_ratings = 0
        self.IMDB_link = "http://www.imdb.com/find?s=tt&q=" + name


#Oscar Category Model
class Oscar(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(100))

    def __init__(self, category):
        self.category = category


#Schemas
class OscarSchema(ma.Schema):
    class Meta:
        fields = ('id', 'category')

oscar_schema = OscarSchema()
oscars_schema = OscarSchema(many=True)


class MovieSchema(ma.Schema):
    oscars = ma.Nested(OscarSchema, many=True)
    class Meta:
        fields = ('id', 'name', 'year', 'description', 'oscars', 'poster', 'rating', 'user_rating', 'num_of_ratings', 'IMDB_link')

movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)
