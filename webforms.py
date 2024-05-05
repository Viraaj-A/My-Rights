from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SelectMultipleField, SubmitField, SelectField, BooleanField
from wtforms.validators import DataRequired, InputRequired, Optional

#Need to replace below with all respondent States, currently for testing
respondent_state_choices = [
    ("Andorra", "Andorra"),
    ("Germany", "Germany"),
    ("Poland", "Poland"),
    ("Bosnia and Herzegovina", "Bosnia and Herzegovina"),
    ("Croatia", "Croatia"),
    ("North Macedonia", "North Macedonia"),
    ("Serbia", "Serbia"),
    ("Slovenia", "Slovenia"),
    ("Cyprus", "Cyprus"),
    ("Russia", "Russia"),
    ("Italy", "Italy"),
    ("Albania", "Albania"),
    ("Luxembourg", "Luxembourg"),
    ("Czech Republic", "Czech Republic"),
    ("Sweden", "Sweden"),
    ("United Kingdom", "United Kingdom"),
    ("Spain", "Spain"),
    ("France", "France"),
    ("Montenegro", "Montenegro"),
    ("Bulgaria", "Bulgaria"),
    ("Romania", "Romania"),
    ("Ireland", "Ireland"),
    ("San Marino", "San Marino"),
    ("Finland", "Finland"),
    ("Portugal", "Portugal"),
    ("Malta", "Malta"),
    ("Ukraine", "Ukraine"),
    ("Liechtenstein", "Liechtenstein"),
    ("Latvia", "Latvia"),
    ("Azerbaijan", "Azerbaijan"),
    ("Greece", "Greece"),
    ("Lithuania", "Lithuania"),
    ("Estonia", "Estonia"),
    ("Slovakia", "Slovakia"),
    ("Iceland", "Iceland"),
    ("Denmark", "Denmark"),
    ("Hungary", "Hungary"),
    ("Norway", "Norway"),
    ("Georgia", "Georgia"),
    ("Belgium", "Belgium"),
    ("Netherlands", "Netherlands"),
    ("Austria", "Austria"),
    ("Türkiye", "Türkiye"),
    ("Republic of Moldova", "Republic of Moldova"),
    ("Switzerland", "Switzerland"),
    ("Armenia", "Armenia")
]

originating_body_choices = [
    ('plenary', 'Court (Plenary)'),
    ('chamber', 'Court (Chamber)'),
    ('sec2', 'Court (Second Section)'),
    ('sec4', 'Court (Fourth Section)'),
    ('com1', 'Court (First Section Committee)'),
    ('com5', 'Court (Fifth Section Committee)'),
    ('sec3', 'Court (Third Section)'),
    ('sec1', 'Court (First Section)'),
    ('sec5', 'Court (Fifth Section)'),
    ('com4', 'Court (Fourth Section Committee)'),
    ('com3', 'Court (Third Section Committee)'),
    ('grand_chamber', 'Court (Grand Chamber)'),
    ('com2', 'Court (Second Section Committee)')
]

importance_level_choices = [
    ('3', '3'),
    ('2', '2'),
    ('key_cases', 'Key cases'),
    ('1', '1')
]

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
    originating_body = SelectMultipleField("Originating Body", choices=originating_body_choices, validators=[Optional()])
    importance_level = SelectMultipleField("Importance Level", choices=importance_level_choices, validators=[Optional()])
    respondent_state = SelectMultipleField("Respondent State", choices=respondent_state_choices, validators=[Optional()])
    date_from = DateField("Date From", format='%Y-%m-%d', validators=[Optional()])
    date_to = DateField("Date To", format='%Y-%m-%d', validators=[Optional()])
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


