import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flaskr.routes import Reviews, ReviewCycle, UserReview, UserList
import unittest
from datetime import datetime
from flask import Flask

class FunctionTests(unittest.TestCase):    
    def test_sanity_check(self):
        self.assertEqual(1 + 1, 2, "Oops")
        
    def test_add_reviewCycle(self):
        r = Reviews(True)
        r.add_reviewCycle("test")
        
        obj = r.store.find(ReviewCycle, ReviewCycle.review_cycle == "test").any()
        
        self.assertIsNotNone(obj)

    def test_only_one_active_reviewCycle(self):
        r = Reviews(True)
        r.add_reviewCycle("test1")
        r.add_reviewCycle("test2")
        r.deactivate_others("test1")
        
        obj1 = r.store.find(ReviewCycle, ReviewCycle.review_cycle == "test1").any().is_active
        obj2 = r.store.find(ReviewCycle, ReviewCycle.review_cycle == "test2").any().is_active
        
        self.assertTrue(obj1)
        self.assertFalse(obj2)

    def test_create_reviews_for_active_users(self):
        r = Reviews(True)
        r.add_reviewCycle("test")
        r.create_reviews_for_active_users("test")
        
        objs = r.store.find(UserReview, UserReview.review_cycle == "test")
        
        self.assertIsNotNone(objs)
        self.assertEqual(objs.count(), 10)
        for i in range(0, 10):
            self.assertEqual(objs[i].review_cycle, "test")
            self.assertEqual(objs[i].date_sent, datetime.now().date())

    def test_create_reviews_for_active_users_one_inactive(self):
        r = Reviews(True)
        r.store.find(UserList, UserList.user_corp_key == "AAA001").set(is_active = False)
        r.add_reviewCycle("test")
        r.create_reviews_for_active_users("test")
        
        objs = r.store.find(UserReview, UserReview.review_cycle == "test")
        
        self.assertIsNotNone(objs)
        self.assertEqual(objs.count(), 9)
        for i in range(0, 9):
            self.assertEqual(objs[i].review_cycle, "test")
            self.assertEqual(objs[i].date_sent, datetime.now().date())

    def test_review_user_is_ok(self):
        r = Reviews(True)
        r.add_reviewCycle("test")
        r.create_reviews_for_active_users("test")
        auth_key = r.store.find(UserReview, UserReview.user_corp_key == "AAA001", UserReview.review_cycle == "test").any().auth_key
        r.review_user("AAA001", auth_key, "y")
        
        obj = r.store.find(UserReview, UserReview.user_corp_key == "AAA001", UserReview.auth_key == auth_key).any()
        
        self.assertEqual(obj.status, "y")
        self.assertEqual(obj.date_received, datetime.now().date())

    def test_review_user_is_not_ok(self):
        r = Reviews(True)
        r.add_reviewCycle("test")
        r.create_reviews_for_active_users("test")
        auth_key = r.store.find(UserReview, UserReview.user_corp_key == "AAA001", UserReview.review_cycle == "test").any().auth_key
        r.review_user("AAA001", auth_key, "n")

        obj1 = r.store.find(UserReview, UserReview.user_corp_key == "AAA001", UserReview.auth_key == auth_key).any()
        obj2 = r.store.find(UserList, UserList.user_corp_key == "AAA001").any()
        
        self.assertEqual(obj1.status, "n")
        self.assertEqual(obj1.date_received, datetime.now().date())
        self.assertFalse(obj2.is_active)

if __name__ == '__main__':
    unittest.main()