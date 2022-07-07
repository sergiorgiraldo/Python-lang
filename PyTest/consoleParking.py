from parking import *

P = Parking()
P.DBWrapper.Setup("./parking.sqlite")

spot = input("What is the spot?")
plate = input("What is the plate?")
starting = input("What is the starting (yyyymmdd hhnn)?")
ending = input("What is the ending (yyyymmdd hhnn)?")

Reservation = ParkingReservation.Create(plate, spot, datetime.strptime(starting, '%Y%m%d %H%M'), datetime.strptime(ending, '%Y%m%d %H%M'))
Msg = P.AddReservation(Reservation)
print("Success" if Msg == "" else Msg)

spot = input("What is the spot?")
plate = input("What is the plate?")
starting = input("What is the starting (yyyymmdd hhnn)?")
ending = input("What is the ending (yyyymmdd hhnn)?")

Reservation = ParkingReservation.Create(plate, spot, datetime.strptime(starting, '%Y%m%d %H%M'), datetime.strptime(ending, '%Y%m%d %H%M'))
Msg = P.AddReservation(Reservation)
print("Success" if Msg == "" else Msg)