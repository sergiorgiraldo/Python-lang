from pony.orm import *
from datetime import datetime

class ParkingReservation:
	def __init__(self, plate, spot, starting, ending):
		self.plate = plate
		self.spot = spot
		self.starting = starting
		self.ending = ending
	
	def Create(plate, spot, starting, ending):
		try:
			ParkingReservation.Validate(plate, spot, starting, ending)
			return ParkingReservation(plate, spot, starting, ending)
		except:
			raise

	def Validate(plate, spot, starting, ending):
		if plate == "":
			raise Exception("plate must be filled")
		if spot == "":
			raise Exception("spot must be filled")
		if starting == "":
			raise Exception("starting must be filled")
		if ending == "":
			raise Exception("ending must be filled")

class DBWrapper:
	db = Database()
	
	def Setup(self, filepath=None):
		if filepath:
			DBWrapper.db.bind(provider="sqlite", filename=filepath)
			DBWrapper.db.generate_mapping()
		else:
			DBWrapper.db.bind(provider="sqlite", filename=":memory:", create_db=True)
			DBWrapper.db.generate_mapping(create_tables=True)
			DBWrapper.GenerateTestData()

	class Parking(db.Entity):
		id_spot = PrimaryKey(int, auto=True)
		spot = Required(str)
	class Reservations(db.Entity):
		id_reservation = PrimaryKey(int, auto=True)
		plate = Required(str)
		starting = Required(datetime)
		ending = Required(datetime)
		id_spot = Required(int)

	@db_session
	def Save(self, ParkingReservation):
		Spot = DBWrapper.Parking.get(spot=ParkingReservation.spot)
		DBWrapper.Reservations(
			id_spot = Spot.id_spot,
			plate = ParkingReservation.plate,
			starting = ParkingReservation.starting,
			ending = ParkingReservation.ending)
		DBWrapper.db.commit()

	@db_session
	def GenerateTestData():
		DBWrapper.Parking(spot = "A1")
		DBWrapper.Parking(spot = "B1")
		DBWrapper.Parking(spot = "A2")
		DBWrapper.Parking(spot = "B2")
		DBWrapper.db.commit()

class Parking:
	def __init__(self):
		self.Spots = ["A1", "A2", "A3", "A4", "A5","B1", "B2", "B3", "B4", "B5"] 
		self.Reservations = []
		self.DBWrapper = DBWrapper()

	def AddReservation(self, ParkingReservation):
		msg = Parking.Validate(self, ParkingReservation);

		if (not msg):
			self.Reservations.append(ParkingReservation)
			self.DBWrapper.Save(ParkingReservation)

		return msg 		

	def Validate(self, ParkingReservation): #dummy logic,evaluate if there is reservation for another car on the day asked, on that spot
		msg = ""
		for reservation in [R for R in self.Reservations if 
				R.starting.date() == datetime.now().date() and 
				R.spot == ParkingReservation.spot]:
			if reservation.plate != ParkingReservation.plate:
				msg = "Another car in the spot today"
		return msg

	def ListAvailableSpots(self): #dummy logic, evaluate if the reservation is on the same day
		AvailableSpots = self.Spots.copy()
		for spot in self.Spots:
			for reservation in [R for R in self.Reservations if 
				spot in R.spot]:
				if reservation.starting.date() == datetime.now().date():
					AvailableSpots.remove(spot)
		return AvailableSpots

	def CountAvailableSpots(self):
		AvailableSpots = Parking.ListAvailableSpots(self)
		return len(AvailableSpots)

	def CheckSpot(self, spot, starting, ending):
		return not any(
		    reservation.starting.date() == starting.date() or reservation.ending.date() == ending.date()
		    for reservation in [R for R in self.Reservations if spot in R.spot])	