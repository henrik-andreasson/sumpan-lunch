from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField, \
    SelectMultipleField, BooleanField, RadioField
from wtforms.fields import DateTimeField
from wtforms.validators import ValidationError, DataRequired, Length
from flask_babel import _, lazy_gettext as _l
from app.main.models import User, LunchResturant, Rating
from datetime import datetime


class EditProfileForm(FlaskForm):
    username = StringField(_l('Username'), validators=[Length(min=2, max=40)])
    about_me = TextAreaField(_l('About me'),
                             validators=[Length(min=0, max=140)])
    submit = SubmitField(_l('Submit'))
    cancel = SubmitField(_l('Cancel'))

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError(_('Please use a different username.'))


class LunchResturantForm(FlaskForm):

    name      = StringField(_l('Name'), validators=[DataRequired()])
    about = StringField(_l('About'))
    location  = StringField(_l('Location (used to find resturant via maps search)'), default="Sundbyberg Sweden")

    submit = SubmitField(_l('Submit'))
    cancel = SubmitField(_l('Cancel'))
    delete = SubmitField(_l('Delete'))


class RatingForm(FlaskForm):

    lunchresturant = SelectField(_l('Lunch Resturant'), validators=[DataRequired()])
    rating = RadioField(_l('Rating'),
                             choices=[(5, _l('Very Good')),
                                      (4, _l('Good')),
                                      (3, _l('OK')),
                                      (2, _l('Bad')),
                                      (1, _l('Very Bad'))],
                             default=3, coerce=int)
    meal = StringField(_l('Meal'))
    comment = StringField(_l('comment'))

    submit = SubmitField(_l('Submit'))
    cancel = SubmitField(_l('Cancel'))
    delete = SubmitField(_l('Delete'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lunchresturant.choices = [(l.id, l.name)
                                for l in LunchResturant.query.order_by(LunchResturant.name).all()]
