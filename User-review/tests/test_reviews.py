import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flaskr.routes import Reviews, ReviewCycle, UserReview, UserList
from datetime import datetime
from assertpy import assert_that

def test_sanity_check():
    assert_that(1 + 1).is_equal_to(2)
    
def test_add_reviewCycle():
    r = Reviews(True)
    r.add_reviewCycle("test")
    
    obj = r.store.find(ReviewCycle, ReviewCycle.review_cycle == "test").any()
    
    assert_that(obj).is_not_none()

def test_only_one_active_reviewCycle():
    r = Reviews(True)
    r.add_reviewCycle("test1")
    r.add_reviewCycle("test2")
    r.deactivate_others("test1")
    
    obj1 = r.store.find(ReviewCycle, ReviewCycle.review_cycle == "test1").any().is_active
    obj2 = r.store.find(ReviewCycle, ReviewCycle.review_cycle == "test2").any().is_active
    
    assert_that(obj1).is_true()
    assert_that(obj2).is_false()

def test_create_reviews_for_active_users():
    r = Reviews(True)
    r.add_reviewCycle("test")
    r.create_reviews_for_active_users("test")
    
    objs = r.store.find(UserReview, UserReview.review_cycle == "test")
    
    assert_that(objs).is_not_none()
    assert_that(objs.count()).is_equal_to(10)
    for i in range(0, 10):
        assert_that(objs[i].review_cycle).is_equal_to("test")
        assert_that(objs[i].date_sent).is_equal_to(datetime.now().date())

def test_create_reviews_for_active_users_one_inactive():
    r = Reviews(True)
    r.store.find(UserList, UserList.user_corp_key == "AAA001").set(is_active = False)
    r.add_reviewCycle("test")
    r.create_reviews_for_active_users("test")
    
    objs = r.store.find(UserReview, UserReview.review_cycle == "test")
    
    assert_that(objs).is_not_none()
    assert_that(objs.count()).is_equal_to(9)
    for i in range(0, 9):
        assert_that(objs[i].review_cycle).is_equal_to("test")
        assert_that(objs[i].date_sent).is_equal_to(datetime.now().date())

def test_review_user_is_ok():
    r = Reviews(True)
    r.add_reviewCycle("test")
    r.create_reviews_for_active_users("test")
    auth_key = r.store.find(UserReview, UserReview.user_corp_key == "AAA001", UserReview.review_cycle == "test").any().auth_key
    r.review_user("AAA001", auth_key, "y")
    
    obj = r.store.find(UserReview, UserReview.user_corp_key == "AAA001", UserReview.auth_key == auth_key).any()
    
    assert_that(obj.status).is_equal_to("y")
    assert_that(obj.date_received).is_equal_to(datetime.now().date())

def test_review_user_is_not_ok():
    r = Reviews(True)
    r.add_reviewCycle("test")
    r.create_reviews_for_active_users("test")
    auth_key = r.store.find(UserReview, UserReview.user_corp_key == "AAA001", UserReview.review_cycle == "test").any().auth_key
    r.review_user("AAA001", auth_key, "n")

    obj1 = r.store.find(UserReview, UserReview.user_corp_key == "AAA001", UserReview.auth_key == auth_key).any()
    obj2 = r.store.find(UserList, UserList.user_corp_key == "AAA001").any()
    
    assert_that(obj1.status).is_equal_to("n")
    assert_that(obj1.date_received).is_equal_to(datetime.now().date())
    assert_that(obj2.is_active).is_false()

def test_hello(client):
    response = client.get("/hello")
    assert_that(response.data.decode("utf-8")).contains("john doe")

def test_create_review_api(client):
    response = client.put("/create_review_cycle", 
                          json={"cycle": "202506"})
    assert_that(response.status_code).is_equal_to(201)