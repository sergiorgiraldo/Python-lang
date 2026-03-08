"""
LeetCode 355: Design Twitter

Pattern: Hash Map (multiple) + Merge K Sorted Streams
Difficulty: Medium
Time Complexity: O(k log k) for getNewsFeed where k = total tweets from followed users
Space Complexity: O(n) for users/tweets/follows
"""

import heapq
from collections import defaultdict


class Twitter:
    """
    Simplified Twitter with follow, unfollow, post and news feed.

    Uses hash maps for user relationships and tweet storage,
    with a merge-K-sorted-lists approach for the news feed.

    The news feed returns the 10 most recent tweets from the user
    and users they follow.

    Example:
        >>> twitter = Twitter()
        >>> twitter.post_tweet(1, 5)
        >>> twitter.get_news_feed(1)
        [5]
    """

    def __init__(self) -> None:
        self.time = 0
        # user_id -> list of (timestamp, tweet_id), most recent last
        self.tweets: dict[int, list[tuple[int, int]]] = defaultdict(list)
        # user_id -> set of followed user_ids
        self.following: dict[int, set[int]] = defaultdict(set)

    def post_tweet(self, user_id: int, tweet_id: int) -> None:
        """User posts a new tweet."""
        self.tweets[user_id].append((self.time, tweet_id))
        self.time += 1

    def get_news_feed(self, user_id: int) -> list[int]:
        """
        Return the 10 most recent tweet IDs from the user and
        users they follow, ordered from most recent to least recent.
        """
        # Collect all relevant users (self + following)
        users = self.following[user_id] | {user_id}

        # Use a max-heap to merge tweets from all followed users
        # Python has a min-heap, so negate timestamps
        heap: list[tuple[int, int, int, int]] = []

        for uid in users:
            user_tweets = self.tweets[uid]
            if user_tweets:
                idx = len(user_tweets) - 1
                ts, tid = user_tweets[idx]
                # (neg_timestamp, tweet_id, user_id, index)
                heapq.heappush(heap, (-ts, tid, uid, idx))

        result: list[int] = []
        while heap and len(result) < 10:
            neg_ts, tid, uid, idx = heapq.heappop(heap)
            result.append(tid)

            # Push the next older tweet from this user
            if idx > 0:
                idx -= 1
                ts, tid = self.tweets[uid][idx]
                heapq.heappush(heap, (-ts, tid, uid, idx))

        return result

    def follow(self, follower_id: int, followee_id: int) -> None:
        """Follower starts following followee."""
        if follower_id != followee_id:
            self.following[follower_id].add(followee_id)

    def unfollow(self, follower_id: int, followee_id: int) -> None:
        """Follower stops following followee."""
        self.following[follower_id].discard(followee_id)


if __name__ == "__main__":
    twitter = Twitter()
    twitter.post_tweet(1, 5)
    print(f"Feed user 1: {twitter.get_news_feed(1)}")  # [5]
    twitter.follow(1, 2)
    twitter.post_tweet(2, 6)
    print(f"Feed user 1: {twitter.get_news_feed(1)}")  # [6, 5]
    twitter.unfollow(1, 2)
    print(f"Feed user 1: {twitter.get_news_feed(1)}")  # [5]
