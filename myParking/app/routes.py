from flask import render_template
from app import app
from .parking import *

@app.route('/')
@app.route('/index')
def index():
    P = Parking()
    P.DBWrapper.Setup("parking.sqlite")
    Reservations = P.GetReservations()
    return render_template('index.html', title='My Parking', reservations=Reservations)