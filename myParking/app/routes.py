from flask import render_template,flash,redirect
from app import app
from app.parking import *
from app.new import NewForm

P = Parking()
P.DBWrapper.Setup("./db/parking.sqlite")

@app.route('/')
@app.route('/index')
def index():
    Reservations = P.GetReservations()
    return render_template('index.html', title='My Parking', reservations=Reservations)

@app.route('/new', methods=['GET', 'POST'])
def new():
    form = NewForm()
    if form.validate_on_submit():
        try:
            P.GetReservations()

            Reservation = ParkingReservation.Create(
                form.plate.data, 
                form.spot.data, 
                datetime.strptime(form.starting.data, '%Y%m%d %H%M'), 
                datetime.strptime(form.ending.data, '%Y%m%d %H%M'))
            Msg = P.AddReservation(Reservation)
            flash(Msg if Msg != "" else "Success!")        
        except Exception as e:
            flash(str(e))

        return redirect('/index')
    return render_template('new.html', title='My Parking', form=form)