from flask_wtf import Form
from wtforms import StringField, SubmitField

class HotelListingsForm(Form):
    city = StringField('City: ')
    checkin = StringField('Checkin: ')
    checkout = StringField('Checkout: ')
    submit = SubmitField('Submit!')