from parking import *
from datetime import datetime, timedelta

now = datetime.now()
startDateToday = datetime(now.year, now.month, now.day, 11, 30)
endDateToday =datetime(now.year, now.month, now.day, 12, 30)
startDateTodayLater = datetime(now.year, now.month, now.day, 13, 30)
endDateTodayLater =datetime(now.year, now.month, now.day, 14, 30)

tomorrow = datetime.now() + timedelta(days=1)
startDateTomorrow = datetime(tomorrow.year, tomorrow.month, tomorrow.day, 11, 30)
endDateTomorrow =datetime(tomorrow.year, tomorrow.month, tomorrow.day, 12, 30)

def test_AddReservation():
    P = Parking()
    firstReservation = ParkingReservation("F1234", "A1", startDateToday, endDateToday)
    P.AddReservation(firstReservation)
    assert len(P.reservations) == 1

def test_AvailabilityFull():
    P = Parking()
    P.reservations.clear()
    assert P.CountAvailableSpots() == len(P.Spots)

def test_AvailabilityJustOne():
    P = Parking()
    firstReservation = ParkingReservation("F1234", "A1", startDateToday, endDateToday)
    msg = P.AddReservation(firstReservation)
    assert P.CountAvailableSpots() == (len(P.Spots) - 1), msg

def test_AvailabilityHasReservationForTomorrow():
    P = Parking()
    firstReservation = ParkingReservation("F1234", "A1", startDateTomorrow, endDateTomorrow)
    P.AddReservation(firstReservation)
    assert len(P.reservations) == 1
    assert P.CountAvailableSpots() == len(P.Spots)

def test_AvailabilityCheckSpot():
    P = Parking()
    assert "A1" in P.ListAvailableSpots()
    firstReservation = ParkingReservation("F1234", "A1", startDateToday, endDateToday)
    P.AddReservation(firstReservation)
    assert "A1" not in P.ListAvailableSpots()

def test_ValidationAcceptSamePlateSameSpot():
    P = Parking()
    firstReservation = ParkingReservation("F1234", "A1", startDateToday, endDateToday)
    msg = P.AddReservation(firstReservation)
    assert (msg == "")

    secondReservation = ParkingReservation("F1234", "A1", startDateTodayLater, endDateTodayLater)
    msg = P.AddReservation(secondReservation)
    assert (msg == "")

    assert len(P.reservations) == 2

def test_CheckIfSpotIsAvailable_Is():
    P = Parking()
    firstReservation = ParkingReservation("F1234", "A1", startDateToday, endDateToday)
    P.AddReservation(firstReservation)
    result = P.CheckSpot("A1", startDateTomorrow, endDateTomorrow)
    assert (result)

def test_CheckIfSpotIsAvailable_IsNot():
    P = Parking()
    firstReservation = ParkingReservation("F1234", "A1", startDateToday, endDateToday)
    P.AddReservation(firstReservation)
    result = P.CheckSpot("A1", startDateToday, endDateToday)
    assert (not result)

def test_ValidationAcceptDifferentPlateDifferentSpot():
    P = Parking()
    firstReservation = ParkingReservation("F1234", "A1", startDateToday, endDateToday)
    msg = P.AddReservation(firstReservation)
    assert (msg == "")

    secondReservation = ParkingReservation("F5678", "A2", startDateToday, endDateToday)
    msg = P.AddReservation(secondReservation)
    assert (msg == "")

    assert len(P.reservations) == 2

def test_ValidationReject():
    P = Parking()
    firstReservation = ParkingReservation("F1234", "A1", startDateToday, endDateToday)
    msg = P.AddReservation(firstReservation)
    assert (msg == "")

    secondReservation = ParkingReservation("F5678", "A1", startDateTodayLater, endDateTodayLater)
    msg = P.AddReservation(secondReservation)
    assert (not msg == "")
    
    assert len(P.reservations) == 1

