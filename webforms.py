from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SelectMultipleField, SubmitField, SelectField, BooleanField
from wtforms.validators import DataRequired, InputRequired

#Need to replace below with all respondent States, currently for testing
respondent_state = ['Germany', 'Romania', 'Spain', 'Russia', 'Ukraine']

#Questions for the questionnaire
physical_string = "Were you physically hurt, touched or harmed?"
procedural_string = "Does your problem link with a legal action?"
mental_string = "Was the person stopped in anyway. For example, was a person stopped from speaking, moving or expressing yourself?"
age_string = "Did the harm involve a child, a person under 18 year of age"
gender_string = "Did the harm relate to gender?"
family_string = "Did the harm relate to a family member of yours?"
community_string = "Did the harm affect more than just yourself?"
nationality_string = "Does the harm relate to your nationality or lack of nationality?"
property_string = "Does the harm relate to property?"

#Search form
class SearchForm(FlaskForm):
    searched = StringField("Searched", validators=[InputRequired()])
    submit = SubmitField("Submit")

#Questionnaire Form
class QuestionnaireForm(FlaskForm):
    physical_q = SelectField(f"{physical_string}", choices=["Yes", "No"], validators=[DataRequired()])
    procedural_q = SelectField(f"{procedural_string}", choices=["Yes", "No"], validators=[DataRequired()])
    mental_q = SelectField(f"{mental_string}", choices=["Yes", "No"], validators=[DataRequired()])
    age_q = SelectField(f"{age_string}", choices=["Yes", "No"], validators=[DataRequired()])
    gender_q = SelectField(f"{gender_string}", choices=["Yes", "No"], validators=[DataRequired()])
    family_q = SelectField(f"{family_string}", choices=["Yes", "No"], validators=[DataRequired()])
    community_q = SelectField(f"{community_string}", choices=["Yes", "No"], validators=[DataRequired()])
    nationality_q = SelectField(f"{nationality_string}", choices=["Yes", "No"], validators=[DataRequired()])
    property_q = SelectField(f"{property_string}", choices=["Yes", "No"], validators=[DataRequired()])
    q_submit = SubmitField("Submit")


