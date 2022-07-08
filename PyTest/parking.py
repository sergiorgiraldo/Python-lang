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
		Spot = DBWrapper.GetSpotByName(spot)
		if Spot == None:
			raise Exception("spot does not exist")

class DBWrapper:
	db = Database()
	
	class Parking(db.Entity):
		id_spot = PrimaryKey(int, auto=True)
		spot = Required(str)
	
	class Reservations(db.Entity):
		id_reservation = PrimaryKey(int, auto=True)
		plate = Required(str)
		starting = Required(datetime)
		ending = Required(datetime)
		id_spot = Required(int)

	def Setup(filepath=None):
		if filepath:
			DBWrapper.db.bind(provider="sqlite", filename=filepath)
			DBWrapper.db.generate_mapping()
		else:
			DBWrapper.db.bind(provider="sqlite", filename=":memory:", create_db=True)
			DBWrapper.db.generate_mapping(create_tables=True)
			DBWrapper.GenerateTestData()

	@db_session
	def Save(ParkingReservation):
		Spot = DBWrapper.GetSpotByName(ParkingReservation.spot)
		DBWrapper.Reservations(
			id_spot = Spot.id_spot,
			plate = ParkingReservation.plate,
			starting = ParkingReservation.starting,
			ending = ParkingReservation.ending)
		DBWrapper.db.commit()

	@db_session
	def GenerateTestData():
		DBWrapper.Parking(spot = "A1")
		DBWrapper.Parking(spot = "A2")
		DBWrapper.Parking(spot = "A3")
		DBWrapper.Parking(spot = "A4")
		DBWrapper.Parking(spot = "A5")
		DBWrapper.Parking(spot = "B1")
		DBWrapper.Parking(spot = "B2")
		DBWrapper.Parking(spot = "B3")
		DBWrapper.Parking(spot = "B4")
		DBWrapper.Parking(spot = "B5")
		DBWrapper.db.commit()

	@db_session
	def GetSpotByName(spotFromReservation):
		Spot = None
		try:
			Spot = DBWrapper.Parking.get(spot=spotFromReservation)
		except:
			pass
		return Spot
			
	@db_session
	def GetSpotById(spotFromReservation):
		Spot = None
		try:
			Spot = DBWrapper.Parking.get(id_spot=spotFromReservation)
		except:
			pass
		return Spot

	@db_session
	def GetSpots():
		aux = []
		for p in select(p for p in DBWrapper.Parking):
			aux.append(p.spot)
		return aux

	@db_session
	def GetReservations():
		aux = []
		for p in select(p for p in DBWrapper.Reservations):
			Spot = DBWrapper.GetSpotById(p.id_spot)
			R = ParkingReservation(p.plate, Spot.spot, p.starting, p.ending)
			aux.append(R)
		return aux

class Parking:
	def __init__(self):
		self.Spots = [] 
		self.Reservations = []
		self.DBWrapper = DBWrapper

	def AddReservation(self, ParkingReservation):
		msg = Parking.Validate(self, ParkingReservation);

		if (not msg):
			self.DBWrapper.Save(ParkingReservation)
			self.Reservations.append(ParkingReservation)

		return msg 		

	def GetSpots(self):
		if len(self.Spots) == 0:
			self.Spots = self.DBWrapper.GetSpots()
		return self.Spots

	def GetReservations(self):
		self.Reservations = self.DBWrapper.GetReservations()
		return self.Reservations

	def Validate(self, ParkingReservation): #dummy logic,evaluate if there is reservation for another car on the day asked, on that spot
		msg = ""
		for reservation in [R for R in self.Reservations if 
				R.starting.date() == datetime.now().date() and 
				R.spot == ParkingReservation.spot]:
			if reservation.plate != ParkingReservation.plate:
				msg = "Another car in the spot today"
		return msg

	def ListAvailableSpots(self): #dummy logic, evaluate if the reservation is on the same day
		AvailableSpots = self.GetSpots().copy()
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
