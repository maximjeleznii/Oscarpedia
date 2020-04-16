from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, HiddenField
from wtforms.validators import DataRequired


class SearchForm(FlaskForm):
    search = StringField('search', validators=[DataRequired()], 
                        render_kw={'class': 'form-control border-0', 'placeholder': 'Search Here'})
    search_field = SelectField(u'Search Type', choices=[('search','All'), ('name', 'Title'), ('year', 'Year'),
                        ('description', 'Description'), ('oscars', 'Oscars'), ('rating', 'Rating'), ('user_rating', 'User Rating')], 
                        default='search', render_kw={'class': 'custom-select btn border-0'})
    submit = SubmitField('Submit', render_kw={'class': 'btn btn-secondary border-0'})


class RatingForm(FlaskForm):
    request_id = HiddenField('Request ID')
    rating = SelectField(u'Rating', choices=[('1', '1'), ('2', '2'), ('3', '3'),
                            ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8'), 
                            ('9', '9'), ('10', '10')], render_kw={'class': 'btn custom-select'})
    submit = SubmitField('Rate', render_kw={'class': 'btn btn-secondary border-0'})