from parking import *
from datetime import datetime, timedelta
from hamcrest import *

now = datetime.now()
startDateToday = datetime(now.year, now.month, now.day, 11, 30)
endDateToday =datetime(now.year, now.month, now.day, 12, 30)
startDateTodayLater = datetime(now.year, now.month, now.day, 13, 30)
endDateTodayLater =datetime(now.year, now.month, now.day, 14, 30)

tomorrow = datetime.now() + timedelta(days=1)
startDateTomorrow = datetime(tomorrow.year, tomorrow.month, tomorrow.day, 11, 30)
endDateTomorrow =datetime(tomorrow.year, tomorrow.month, tomorrow.day, 12, 30)
    
firstReservation = ParkingReservation("F1234", "A1", startDateToday, endDateToday)

def test_AddReservation():
    P = Parking()
    P.AddReservation(firstReservation)
    assert_that(len(P.reservations), is_(1))

def test_AvailabilityFull():
    P = Parking()
    P.reservations.clear()
    assert_that(P.CountAvailableSpots(), equal_to(len(P.Spots)))

def test_AvailabilityJustOne():
    P = Parking()
    P.AddReservation(firstReservation)
    assert_that(P.CountAvailableSpots(), equal_to(len(P.Spots) -1))

def test_AvailabilityHasReservationForTomorrow():
    P = Parking()
    otherReservation = ParkingReservation("F1234", "A1", startDateTomorrow, endDateTomorrow)
    P.AddReservation(otherReservation)
    assert_that(len(P.reservations), is_(1))
    assert_that(P.CountAvailableSpots(), equal_to(len(P.Spots)))

def test_AvailabilityCheckSpot():
    P = Parking()
    assert_that("A1", is_in(P.ListAvailableSpots())) 
    P.AddReservation(firstReservation)
    assert_that("A1", not is_in(P.ListAvailableSpots())) 

def test_ValidationAcceptSamePlateSameSpot():
    P = Parking()
    msg = P.AddReservation(firstReservation)
    assert_that(msg, is_(""))

    otherReservation = ParkingReservation("F1234", "A1", startDateTodayLater, endDateTodayLater)
    msg = P.AddReservation(otherReservation)
    assert_that(msg, is_(""))
    assert_that(len(P.reservations), is_(2))

def test_CheckIfSpotIsAvailable_Is():
    P = Parking()
    P.AddReservation(firstReservation)
    spotIsAvailable = P.CheckSpot("A1", startDateTomorrow, endDateTomorrow)
    assert_that(spotIsAvailable)

def test_CheckIfSpotIsAvailable_IsNot():
    P = Parking()
    P.AddReservation(firstReservation)
    spotAvailable = P.CheckSpot("A1", startDateToday, endDateToday)
    assert_that(is_not(spotAvailable))

def test_ValidationAcceptDifferentPlateDifferentSpot():
    P = Parking()
    msg = P.AddReservation(firstReservation)
    assert_that(msg, is_(""))

    otherReservation = ParkingReservation("F5678", "A2", startDateToday, endDateToday)
    msg = P.AddReservation(otherReservation)
    assert_that(msg, is_(""))

    assert_that(len(P.reservations), is_(2))

def test_ValidationReject():
    P = Parking()
    msg = P.AddReservation(firstReservation)
    assert_that(msg, is_(""))

    otherReservation = ParkingReservation("F5678", "A1", startDateTodayLater, endDateTodayLater)
    msg = P.AddReservation(otherReservation)
    assert_that(msg, is_not(""))
    
    assert_that(len(P.reservations), is_(1))

