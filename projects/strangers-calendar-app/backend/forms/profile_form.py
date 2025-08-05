|
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class ProfileForm(FlaskForm):
bio = StringField('Bio', validators=[DataRequired()])
profile_picture_url = StringField('Profile Picture URL')
submit = SubmitField('Save Profile')