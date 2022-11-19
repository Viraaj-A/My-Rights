from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, SelectMultipleField, widgets, SubmitField
from wtforms.validators import DataRequired, InputRequired

#Need to replace below with all respondent States, currently for testing
respondent_state = ['Germany', 'Romania', 'Spain', 'Russia', 'Ukraine']


#Create search form
class SearchForm(FlaskForm):
    searched = StringField("Searched", validators=[InputRequired()])
    start_date = DateField('Start Date', format='%Y-%m-%d')
    end_date = DateField('End Date', format='%Y-%m-%d')
    importance = SelectMultipleField('Importance', choices=[
                                    ('Key cases', 'Key Case'),
                                    ('3','3'),
                                    ('2', '2'),
                                    ('1', '1')
                                     ])
    respondent = SelectMultipleField('Country', choices=respondent_state)
    submit = SubmitField("Submit")


