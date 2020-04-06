from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class SearchForm(FlaskForm):
    search = StringField('search', validators=[DataRequired()], 
                        render_kw={'class': 'form-control-sm', 'placeholder': 'Search Here'})
    submit = SubmitField('Submit', render_kw={'class': 'btn-sm btn-success'})