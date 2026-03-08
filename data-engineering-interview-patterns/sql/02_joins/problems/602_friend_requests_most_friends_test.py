"""Tests for LeetCode 602: Friend Requests II - Who Has the Most Friends."""

from pathlib import Path

from helpers import run_sql_file_df

PROBLEM_DIR = Path(__file__).parent


class TestFriendRequestsMostFriends:

    def test_basic(self, db_friend_request) -> None:
        db_friend_request.execute("""
            INSERT INTO RequestAccepted (requester_id, accepter_id, accept_date) VALUES
                (1, 2, '2016-06-03'),
                (1, 3, '2016-06-08'),
                (2, 3, '2016-06-08'),
                (3, 4, '2016-06-09');
        """)
        result = run_sql_file_df(
            db_friend_request,
            PROBLEM_DIR / "602_friend_requests_most_friends.sql",
        )
        # Person 3 has 3 friends (1, 2, 4)
        assert len(result) == 1
        assert result[0]["id"] == 3
        assert result[0]["num"] == 3

    def test_both_sides_counted(self, db_friend_request) -> None:
        """Person appearing as both requester and accepter."""
        db_friend_request.execute("""
            INSERT INTO RequestAccepted (requester_id, accepter_id, accept_date) VALUES
                (1, 2, '2016-06-03'),
                (3, 1, '2016-06-08');
        """)
        result = run_sql_file_df(
            db_friend_request,
            PROBLEM_DIR / "602_friend_requests_most_friends.sql",
        )
        # Person 1 has 2 friends (as requester: 2, as accepter: 3)
        assert result[0]["id"] == 1
        assert result[0]["num"] == 2

    def test_single_friendship(self, db_friend_request) -> None:
        db_friend_request.execute("""
            INSERT INTO RequestAccepted (requester_id, accepter_id, accept_date) VALUES
                (1, 2, '2016-06-03');
        """)
        result = run_sql_file_df(
            db_friend_request,
            PROBLEM_DIR / "602_friend_requests_most_friends.sql",
        )
        # Both have 1 friend, LIMIT 1 returns either
        assert result[0]["num"] == 1
        assert result[0]["id"] in (1, 2)

    def test_clear_winner(self, db_friend_request) -> None:
        db_friend_request.execute("""
            INSERT INTO RequestAccepted (requester_id, accepter_id, accept_date) VALUES
                (1, 2, '2016-06-01'),
                (1, 3, '2016-06-02'),
                (1, 4, '2016-06-03'),
                (1, 5, '2016-06-04'),
                (2, 3, '2016-06-05');
        """)
        result = run_sql_file_df(
            db_friend_request,
            PROBLEM_DIR / "602_friend_requests_most_friends.sql",
        )
        # Person 1 has 4 friends (2, 3, 4, 5)
        assert result[0]["id"] == 1
        assert result[0]["num"] == 4
