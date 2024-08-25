from flask import current_app, request, jsonify, Blueprint
from storm.locals import *
from datetime import datetime, timedelta
import uuid

bp = Blueprint("routes", __name__, url_prefix="/")

class UserList(object):
    __storm_table__ = "tbl_user_list"
    __storm_primary__ = "user_corp_key"
    user_corp_key = Unicode()
    is_active = Bool()


class ReviewCycle(object):
    __storm_table__ = "tbl_user_review_cycle"
    __storm_primary__ = "review_cycle"
    review_cycle = Unicode()
    is_active = Bool()


class UserReview(object):
    __storm_table__ = "tbl_user_review"
    __storm_primary__ = "user_corp_key", "review_cycle"
    user_corp_key = Unicode()
    review_cycle = Unicode()
    auth_key = Unicode()
    date_sent = Date()
    date_received = Date()
    status = Unicode()


class Reviews:
    testing = False

    def __init__(self, testing=False):
        self.testing = testing
        self.connect_to_database()

    def connect_to_database(self):
        if self.testing:
            db = create_database("sqlite:")
            self.store = Store(db)
            # note: this is being executed only through the unit tests and the unit tests
            # position itself in the root folder (see the sys.path in the top of the file)
            # that"s why I use the path as ./
            with open("./ddl/tbl-user-review-cycle.sql", "r") as f:
                self.store.execute(f.read() + ";")
            with open("./ddl/tbl-user-list.sql", "r") as f:
                self.store.execute(f.read() + ";")
            with open("./ddl/tbl-user-review.sql", "r") as f:
                self.store.execute(f.read() + ";")
            with open("./ddl/insert-users.sql", "r") as f:
                for line in f:
                    self.store.execute(line)
            self.store.commit()
        else:
            db = create_database("postgres://GK47LX@localhost:5432/mine")
            self.store = Store(db)

    def add_reviewCycle(self, cycle):
        reviewCycle = ReviewCycle()
        reviewCycle.review_cycle = cycle
        reviewCycle.is_active = True
        self.store.add(reviewCycle)
        self.store.commit()

    def deactivate_others(self, cycle):
        self.store.find(ReviewCycle, ReviewCycle.review_cycle !=
                        cycle).set(is_active=False)
        self.store.commit()

    def create_reviews_for_active_users(self, cycle):
        users = self.store.find(UserList, UserList.is_active == True)
        for user in users:
            review = UserReview()
            review.user_corp_key = user.user_corp_key
            review.review_cycle = cycle
            review.auth_key = str(uuid.uuid4())
            review.date_sent = datetime.now()
            self.store.add(review)
        self.store.commit()

    def review_user(self, user, auth_key, status):
        self.store.find(UserReview, UserReview.user_corp_key == user, UserReview.auth_key == auth_key).set(
            status=status, date_received=datetime.now())

        if status in ["n"]:
            self.store.find(UserList, UserList.user_corp_key ==
                            user).set(is_active=False)

        self.store.commit()

    def handle_active_review(self):
        current_cycle = self.store.find(
            ReviewCycle, ReviewCycle.is_active == True).any().review_cycle
        reviews = self.store.find(
            UserReview, UserReview.review_cycle == current_cycle)
        for review in reviews:
            if review.date_received is None:
                if datetime.now().date() - review.date_sent > timedelta(days=15):
                    self.store.find(UserList, UserList.user_corp_key == review.user_corp_key).set(
                        is_active=False)
        self.store.commit()

@bp.route("/user_review", methods=["POST"])
def user_review():
    data = request.json
    if not all(key in data for key in ["user", "auth-key", "status"]):
        return jsonify({"error": "Missing required fields"}), 400

    if data["status"] not in ["y", "n"]:
        return jsonify({"error": "Invalid status, should be y or n"}), 400

    try:
        r = Reviews(current_app.testing)

        r.review_user(data["user"], data["auth-key"], data["status"])

        return jsonify({"message": "Review submitted successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# TODO: SEND EMAIL TO USERS AND LINE MANAGERS


@bp.route("/create_review_cycle", methods=["PUT"])
def create_review_cycle():
    data = request.json
    if "cycle" not in data:
        return jsonify({"error": "Missing "cycle" field"}), 400

    try:
        r = Reviews(current_app.testing)

        r.add_reviewCycle(data["cycle"])

        r.deactivate_others(data["cycle"])

        r.create_reviews_for_active_users(data["cycle"])

        return jsonify({"message": "Review cycle created successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# TODO: SCHEDULE TO RUN DAILY
@bp.route("/handle_reviews", methods=["POST"])
def handle_reviews():
    try:
        r = Reviews(current_app.testing)

        r.handle_active_review()

        return jsonify({"message": "Reviews handled successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

