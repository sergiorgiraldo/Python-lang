"""Tests for LeetCode 355: Design Twitter."""

from p355_design_twitter import Twitter


class TestTwitter:
    """Test the Twitter design."""

    def test_post_and_feed(self):
        """User sees their own tweets."""
        t = Twitter()
        t.post_tweet(1, 5)
        assert t.get_news_feed(1) == [5]

    def test_follow_and_feed(self):
        """User sees followed user's tweets."""
        t = Twitter()
        t.post_tweet(1, 5)
        t.follow(1, 2)
        t.post_tweet(2, 6)
        assert t.get_news_feed(1) == [6, 5]

    def test_unfollow(self):
        """Unfollowing removes their tweets from feed."""
        t = Twitter()
        t.post_tweet(1, 5)
        t.follow(1, 2)
        t.post_tweet(2, 6)
        t.unfollow(1, 2)
        assert t.get_news_feed(1) == [5]

    def test_feed_ordering(self):
        """Most recent tweets come first."""
        t = Twitter()
        t.post_tweet(1, 1)
        t.post_tweet(1, 2)
        t.post_tweet(1, 3)
        assert t.get_news_feed(1) == [3, 2, 1]

    def test_feed_limit_10(self):
        """Feed returns at most 10 tweets."""
        t = Twitter()
        for i in range(15):
            t.post_tweet(1, i)
        feed = t.get_news_feed(1)
        assert len(feed) == 10
        assert feed == [14, 13, 12, 11, 10, 9, 8, 7, 6, 5]

    def test_empty_feed(self):
        """User with no tweets and no follows gets empty feed."""
        t = Twitter()
        assert t.get_news_feed(1) == []

    def test_follow_self_ignored(self):
        """Following yourself should be a no-op."""
        t = Twitter()
        t.follow(1, 1)
        t.post_tweet(1, 5)
        # Should still see own tweet exactly once
        assert t.get_news_feed(1) == [5]

    def test_unfollow_non_followed(self):
        """Unfollowing someone you don't follow should not error."""
        t = Twitter()
        t.unfollow(1, 2)  # should not raise

    def test_multiple_users_merged(self):
        """Feed merges tweets from multiple followed users in order."""
        t = Twitter()
        t.follow(1, 2)
        t.follow(1, 3)
        t.post_tweet(2, 10)  # oldest
        t.post_tweet(3, 20)
        t.post_tweet(2, 30)
        t.post_tweet(1, 40)  # newest
        assert t.get_news_feed(1) == [40, 30, 20, 10]

    def test_leetcode_example(self):
        """Full LeetCode example sequence."""
        t = Twitter()
        t.post_tweet(1, 5)
        assert t.get_news_feed(1) == [5]
        t.follow(1, 2)
        t.post_tweet(2, 6)
        assert t.get_news_feed(1) == [6, 5]
        t.unfollow(1, 2)
        assert t.get_news_feed(1) == [5]
