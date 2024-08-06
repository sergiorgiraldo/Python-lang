import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flaskr.routes import Reviews, ReviewCycle, UserReview, UserList
from datetime import datetime

def test_sanity_check():
    assert 1 + 1 == 2
    
def test_add_reviewCycle():
    r = Reviews(True)
    r.add_reviewCycle("test")
    
    obj = r.store.find(ReviewCycle, ReviewCycle.review_cycle == "test").any()
    
    assert obj is not None

def test_only_one_active_reviewCycle():
    r = Reviews(True)
    r.add_reviewCycle("test1")
    r.add_reviewCycle("test2")
    r.deactivate_others("test1")
    
    obj1 = r.store.find(ReviewCycle, ReviewCycle.review_cycle == "test1").any().is_active
    obj2 = r.store.find(ReviewCycle, ReviewCycle.review_cycle == "test2").any().is_active
    
    assert obj1 == True
    assert obj2 == False

def test_create_reviews_for_active_users():
    r = Reviews(True)
    r.add_reviewCycle("test")
    r.create_reviews_for_active_users("test")
    
    objs = r.store.find(UserReview, UserReview.review_cycle == "test")
    
    assert objs is not None
    assert objs.count() == 10
    for i in range(0, 10):
        assert objs[i].review_cycle == "test"
        assert objs[i].date_sent == datetime.now().date()

def test_create_reviews_for_active_users_one_inactive():
    r = Reviews(True)
    r.store.find(UserList, UserList.user_corp_key == "AAA001").set(is_active = False)
    r.add_reviewCycle("test")
    r.create_reviews_for_active_users("test")
    
    objs = r.store.find(UserReview, UserReview.review_cycle == "test")
    
    assert objs is not None
    assert objs.count() == 9
    for i in range(0, 9):
        assert objs[i].review_cycle == "test"
        assert objs[i].date_sent == datetime.now().date()

def test_review_user_is_ok():
    r = Reviews(True)
    r.add_reviewCycle("test")
    r.create_reviews_for_active_users("test")
    auth_key = r.store.find(UserReview, UserReview.user_corp_key == "AAA001", UserReview.review_cycle == "test").any().auth_key
    r.review_user("AAA001", auth_key, "y")
    
    obj = r.store.find(UserReview, UserReview.user_corp_key == "AAA001", UserReview.auth_key == auth_key).any()
    
    assert obj.status == "y"
    assert obj.date_received == datetime.now().date()

def test_review_user_is_not_ok():
    r = Reviews(True)
    r.add_reviewCycle("test")
    r.create_reviews_for_active_users("test")
    auth_key = r.store.find(UserReview, UserReview.user_corp_key == "AAA001", UserReview.review_cycle == "test").any().auth_key
    r.review_user("AAA001", auth_key, "n")

    obj1 = r.store.find(UserReview, UserReview.user_corp_key == "AAA001", UserReview.auth_key == auth_key).any()
    obj2 = r.store.find(UserList, UserList.user_corp_key == "AAA001").any()
    
    assert obj1.status == "n"
    assert obj1.date_received == datetime.now().date()
    assert obj2.is_active == False

def test_hello(client):
    response = client.get("/hello")
    assert b"hello world" in response.data
    assert b"doe" in response.data

def test_create_review_api(client):
    response = client.put("/create_review_cycle", 
                          json={"cycle": "202506"})
    assert response.status_code == 201