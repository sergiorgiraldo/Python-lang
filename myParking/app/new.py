from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField

class NewForm(FlaskForm):
    plate = StringField('plate')
    spot = StringField('spot')
    starting = StringField('starting', render_kw={"placeholder": "yyyymmdd hhnn"})
    ending = StringField('ending', render_kw={"placeholder": "yyyymmdd hhnn"})
    submit = SubmitField('Reserve')