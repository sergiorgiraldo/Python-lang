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
    
firstReservation = ParkingReservation.Create("F1234", "A1", startDateToday, endDateToday)

def TearDown(Parking):
    Parking.DBWrapper.db.provider = None
    Parking.DBWrapper.db.schema = None

def test_CreateReservation():
    result = ParkingReservation.Create("F1234", "A1", startDateToday, endDateToday)    
    assert_that(result, instance_of(ParkingReservation))

def test_CreateReservationWithoutPlate_ThrowsException():
    assert_that(
        calling(ParkingReservation.Create).
            with_args("", "A1", startDateToday, endDateToday), 
        raises (Exception, "plate must be filled"))

def test_CreateReservationWithoutSpot_ThrowsException():
    assert_that(
        calling(ParkingReservation.Create).
            with_args("F1234", "", startDateToday, endDateToday), 
        raises (Exception, "spot must be filled"))

def test_CreateReservationWithoutStarting_ThrowsException():
    assert_that(
        calling(ParkingReservation.Create).
            with_args("F1234", "A1", "", endDateToday), 
        raises (Exception, "starting must be filled"))

def test_CreateReservationWithoutEnding_ThrowsException():
    assert_that(
        calling(ParkingReservation.Create).
            with_args("F1234", "A1", startDateToday, ""), 
        raises (Exception, "ending must be filled"))


def test_AddReservation():
    P = Parking()
    P.DBWrapper.Setup()
    P.AddReservation(firstReservation)
    assert_that(len(P.Reservations), is_(1))

def test_AvailabilityFull():
    P = Parking()
    P.Reservations.clear()
    TearDown(P)
    assert_that(P.CountAvailableSpots(), equal_to(len(P.Spots)))

def test_AvailabilityJustOne():
    P = Parking()
    P.DBWrapper.Setup()
    P.AddReservation(firstReservation)
    TearDown(P)
    assert_that(P.CountAvailableSpots(), equal_to(len(P.Spots) -1))

def test_AvailabilityHasReservationForTomorrow():
    P = Parking()
    P.DBWrapper.Setup()
    otherReservation = ParkingReservation.Create("F1234", "A1", startDateTomorrow, endDateTomorrow)
    P.AddReservation(otherReservation)
    TearDown(P)
    assert_that(len(P.Reservations), is_(1))
    assert_that(P.CountAvailableSpots(), equal_to(len(P.Spots)))

def test_AvailabilityCheckSpot():
    P = Parking()
    P.DBWrapper.Setup()
    assert_that("A1", is_in(P.ListAvailableSpots())) 
    P.AddReservation(firstReservation)
    TearDown(P)
    assert_that("A1", not is_in(P.ListAvailableSpots())) 

def test_ValidationAcceptSamePlateSameSpot():
    P = Parking()
    P.DBWrapper.Setup()
    msg = P.AddReservation(firstReservation)
    assert_that(msg, is_(""))

    otherReservation = ParkingReservation("F1234", "A1", startDateTodayLater, endDateTodayLater)
    msg = P.AddReservation(otherReservation)
    TearDown(P)
    assert_that(msg, is_(""))
    assert_that(len(P.Reservations), is_(2))

def test_CheckIfSpotIsAvailable_Is():
    P = Parking()
    P.DBWrapper.Setup()
    P.AddReservation(firstReservation)
    spotIsAvailable = P.CheckSpot("A1", startDateTomorrow, endDateTomorrow)
    TearDown(P)
    assert_that(spotIsAvailable)

def test_CheckIfSpotIsAvailable_IsNot():
    P = Parking()
    P.DBWrapper.Setup()
    P.AddReservation(firstReservation)
    spotAvailable = P.CheckSpot("A1", startDateToday, endDateToday)
    TearDown(P)
    assert_that(is_not(spotAvailable))

def test_ValidationAcceptDifferentPlateDifferentSpot():
    P = Parking()
    P.DBWrapper.Setup()
    msg = P.AddReservation(firstReservation)
    assert_that(msg, is_(""))

    otherReservation = ParkingReservation.Create("F5678", "A2", startDateToday, endDateToday)
    msg = P.AddReservation(otherReservation)
    assert_that(msg, is_(""))

    TearDown(P)
    assert_that(len(P.Reservations), is_(2))

def test_ValidationReject():
    P = Parking()
    P.DBWrapper.Setup()
    msg = P.AddReservation(firstReservation)
    assert_that(msg, is_(""))

    otherReservation = ParkingReservation.Create("F5678", "A1", startDateTodayLater, endDateTodayLater)
    msg = P.AddReservation(otherReservation)
    assert_that(msg, is_not(""))
    
    TearDown(P)
    assert_that(len(P.Reservations), is_(1))
