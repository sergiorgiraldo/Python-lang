from app.parking import *
from datetime import datetime, timedelta
from hamcrest import *
import pytest

now = datetime.now()
startDateToday = datetime(now.year, now.month, now.day, 11, 30)
endDateToday =datetime(now.year, now.month, now.day, 12, 30)
startDateTodayLater = datetime(now.year, now.month, now.day, 13, 30)
endDateTodayLater =datetime(now.year, now.month, now.day, 14, 30)

tomorrow = datetime.now() + timedelta(days=1)
startDateTomorrow = datetime(tomorrow.year, tomorrow.month, tomorrow.day, 11, 30)
endDateTomorrow =datetime(tomorrow.year, tomorrow.month, tomorrow.day, 12, 30)
    
@pytest.fixture
def Parking_(): 
    P = Parking()
    P.DBWrapper.db.provider = None
    P.DBWrapper.db.schema = None
    P.DBWrapper.Setup()
    return P

@pytest.fixture
def PrepareTest(Parking_): #not using it, this is the proper way to use a setup (Parking_) and also have pre/post actions
    print("before each test")
    yield
    print("after each teste")

def test_CreateReservation(Parking_, PrepareTest):
    result = ParkingReservation.Create("F1234", "A1", startDateToday, endDateToday)    
    assert_that(result, instance_of(ParkingReservation))    

def test_CreateReservationWithoutPlate_ThrowsException(Parking_, PrepareTest):
    assert_that(
        calling(ParkingReservation.Create).
            with_args("", "A1", startDateToday, endDateToday), 
        raises (Exception, "plate must be filled"))

def test_CreateReservationWithoutSpot_ThrowsException(Parking_, PrepareTest):
    assert_that(
        calling(ParkingReservation.Create).
            with_args("F1234", "", startDateToday, endDateToday), 
        raises (Exception, "spot must be filled"))

def test_CreateReservationWithoutStarting_ThrowsException(Parking_, PrepareTest):
    assert_that(
        calling(ParkingReservation.Create).
            with_args("F1234", "A1", "", endDateToday), 
        raises (Exception, "starting must be filled"))

def test_CreateReservationWithoutEnding_ThrowsException(Parking_, PrepareTest):
    assert_that(
        calling(ParkingReservation.Create).
            with_args("F1234", "A1", startDateToday, ""), 
        raises (Exception, "ending must be filled"))

def test_AddReservation(Parking_, PrepareTest):
    firstReservation = ParkingReservation.Create("F1234", "A1", startDateToday, endDateToday)
    Parking_.AddReservation(firstReservation)
    assert_that(len(Parking_.Reservations), is_(1))

def test_AvailabilityFull(Parking_, PrepareTest):
    Parking_.Reservations.clear()
    assert_that(Parking_.CountAvailableSpots(), equal_to(len(Parking_.GetSpots())))

def test_AvailabilityJustOne(Parking_, PrepareTest):
    firstReservation = ParkingReservation.Create("F1234", "A1", startDateToday, endDateToday)
    Parking_.AddReservation(firstReservation)
    assert_that(Parking_.CountAvailableSpots(), equal_to(len(Parking_.GetSpots()) -1))

def test_SpotMustExist(Parking_, PrepareTest):
    assert_that(
        calling(ParkingReservation.Create).
            with_args("F1234", "THIS DOES NOT EXIST", startDateTodayLater, endDateTodayLater), 
        raises (Exception, "spot does not exist"))

def test_AvailabilityHasReservationForTomorrow(Parking_, PrepareTest):
    otherReservation = ParkingReservation.Create("F1234", "A1", startDateTomorrow, endDateTomorrow)
    Parking_.AddReservation(otherReservation)
    assert_that(len(Parking_.Reservations), is_(1))
    assert_that(Parking_.CountAvailableSpots(), equal_to(len(Parking_.GetSpots())))

def test_AvailabilityCheckSpot(Parking_, PrepareTest):
    firstReservation = ParkingReservation.Create("F1234", "A1", startDateToday, endDateToday)
    assert_that("A1", is_in(Parking_.ListAvailableSpots())) 
    Parking_.AddReservation(firstReservation)
    assert_that("A1", not is_in(Parking_.ListAvailableSpots())) 

def test_ValidationAcceptSamePlateSameSpot(Parking_, PrepareTest):
    firstReservation = ParkingReservation.Create("F1234", "A1", startDateToday, endDateToday)
    msg = Parking_.AddReservation(firstReservation)
    assert_that(msg, is_(""))

    otherReservation = ParkingReservation.Create("F1234", "A1", startDateTodayLater, endDateTodayLater)
    msg = Parking_.AddReservation(otherReservation)
    assert_that(msg, is_(""))
    assert_that(len(Parking_.Reservations), is_(2))

def test_CheckIfSpotIsAvailable_Is(Parking_, PrepareTest):
    firstReservation = ParkingReservation.Create("F1234", "A1", startDateToday, endDateToday)
    Parking_.AddReservation(firstReservation)
    spotIsAvailable = Parking_.CheckSpot("A1", startDateTomorrow, endDateTomorrow)
    assert_that(spotIsAvailable)

def test_CheckIfSpotIsAvailable_IsNot(Parking_, PrepareTest):
    firstReservation = ParkingReservation.Create("F1234", "A1", startDateToday, endDateToday)
    Parking_.AddReservation(firstReservation)
    spotAvailable = Parking_.CheckSpot("A1", startDateToday, endDateToday)
    assert_that(is_not(spotAvailable))

def test_ValidationAcceptDifferentPlateDifferentSpot(Parking_, PrepareTest):
    firstReservation = ParkingReservation.Create("F1234", "A1", startDateToday, endDateToday)
    msg = Parking_.AddReservation(firstReservation)
    assert_that(msg, is_(""))

    otherReservation = ParkingReservation.Create("F5678", "A2", startDateToday, endDateToday)
    msg = Parking_.AddReservation(otherReservation)
    assert_that(msg, is_(""))

    assert_that(len(Parking_.Reservations), is_(2))

def test_ValidationReject(Parking_, PrepareTest):
    firstReservation = ParkingReservation.Create("F1234", "A1", startDateToday, endDateToday)
    msg = Parking_.AddReservation(firstReservation)
    assert_that(msg, is_(""))

    otherReservation = ParkingReservation.Create("F5678", "A1", startDateTodayLater, endDateTodayLater)
    msg = Parking_.AddReservation(otherReservation)
    assert_that(msg, is_not(""))
    
    assert_that(len(Parking_.Reservations), is_(1))