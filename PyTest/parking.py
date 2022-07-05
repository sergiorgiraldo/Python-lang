from datetime import datetime

class ParkingReservation:
	def __init__(self, plate, spot, starting, ending):
		self.plate = plate
		self.spot = spot
		self.starting = starting
		self.ending = ending

class Parking:
	def __init__(self):
		self.Spots = ["A1", "A2", "A3", "A4", "A5","B1", "B2", "B3", "B4", "B5"] 
		self.reservations = []

	def AddReservation(self, ParkingReservation):
		msg = Parking.Validate(self, ParkingReservation);

		if (not msg):
			self.reservations.append(ParkingReservation)
		
		return msg 

	def Validate(self, ParkingReservation): #dummy logic,evaluate if there is reservation for another car on the day asked, on that spot
		msg = ""
		for reservation in [R for R in self.reservations if 
				R.starting.date() == datetime.now().date() and 
				R.spot == ParkingReservation.spot]:
			if reservation.plate != ParkingReservation.plate:
				msg = "Another car in the spot today"
		return msg

	def ListAvailableSpots(self): #dummy logic, evaluate if the reservation is on the same day
		AvailableSpots = self.Spots.copy()
		for spot in self.Spots:
			for reservation in [R for R in self.reservations if 
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
		    for reservation in [R for R in self.reservations if spot in R.spot])	