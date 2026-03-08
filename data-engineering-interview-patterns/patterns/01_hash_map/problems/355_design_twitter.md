# Design Twitter (LeetCode #355)

🔗 [LeetCode 355: Design Twitter](https://leetcode.com/problems/design-twitter/)

> **Difficulty:** Medium | **Interview Frequency:** Occasional

## Problem Statement

Design a simplified Twitter that supports:
- `postTweet(userId, tweetId)` - Post a new tweet.
- `getNewsFeed(userId)` - Return the 10 most recent tweet IDs from the user and people they follow. Ordered most recent first.
- `follow(followerId, followeeId)` - Follower follows followee.
- `unfollow(followerId, followeeId)` - Follower unfollows followee.

**Example:**
```
twitter = Twitter()
twitter.postTweet(1, 5)
twitter.getNewsFeed(1)       // [5]
twitter.follow(1, 2)
twitter.postTweet(2, 6)
twitter.getNewsFeed(1)       // [6, 5]
twitter.unfollow(1, 2)
twitter.getNewsFeed(1)       // [5]
```

---

## Thought Process

1. **Data storage** - Need to track tweets per user and follow relationships. Both are hash map problems.
2. **The interesting part is the news feed.** We need to merge tweets from multiple users, sorted by time, and return the top 10.
3. **This is Merge K Sorted Lists** - Each user's tweet list is sorted by time. Merging K sorted lists is a classic heap problem.
4. **Optimization** - We only need the top 10, so we don't merge everything. We use a heap and stop after 10 elements.

---

## Worked Example

Twitter's news feed merges tweets from multiple users into one chronological stream. This uses multiple dicts working together: one mapping user IDs to their tweet lists, another mapping user IDs to the set of users they follow. The feed pulls from the current user's tweets plus all followed users' tweets, sorted by timestamp.

The merge step uses a K-way merge with a heap (pattern 05), where K is the number of users being merged. But the hash maps are what make the follow/unfollow operations O(1) and the tweet lookups O(1).

```
Twitter()

postTweet(1, 101):  User 1 posts tweet 101 (time=0)
postTweet(2, 201):  User 2 posts tweet 201 (time=1)
postTweet(1, 102):  User 1 posts tweet 102 (time=2)
postTweet(3, 301):  User 3 posts tweet 301 (time=3)

Internal state (two dicts):
  tweets = {
    1: [(time=0, id=101), (time=2, id=102)],
    2: [(time=1, id=201)],
    3: [(time=3, id=301)]
  }
  following = {1: set(), 2: set(), 3: set()}

getNewsFeed(1) → [102, 101]:
  User 1 follows nobody. Feed = only user 1's tweets.
  Sort by time (newest first): [102, 101]

follow(1, 2):  following[1].add(2) → following[1] = {2}
follow(1, 3):  following[1].add(3) → following[1] = {2, 3}
  Both are O(1) set operations.

getNewsFeed(1) → [301, 102, 201, 101]:
  Gather tweets from self + followed users:
    User 1's tweets: [(t=2, 102), (t=0, 101)]
    User 2's tweets: [(t=1, 201)]
    User 3's tweets: [(t=3, 301)]
  Merge all by timestamp (newest first):
    t=3: 301 → t=2: 102 → t=1: 201 → t=0: 101
  Return up to 10 most recent: [301, 102, 201, 101]

unfollow(1, 3):  following[1].discard(3) → following[1] = {2}
  O(1) set removal.

getNewsFeed(1) → [102, 201, 101]:
  Now merging only user 1 and user 2's tweets.
  User 3's tweet (301) no longer appears.

The key data structure decisions:
  - tweets dict: O(1) to find any user's tweet list
  - following set: O(1) to follow, unfollow or check "does user 1 follow user 2?"
  - Heap for merge: O(m log k) to merge k users' tweets and return the top m
```

---

## Approaches

<details>
<summary>💡 Hint</summary>

Each user's tweets are already in chronological order. Getting the 10 most recent across all followed users is like merging K sorted lists and taking the first 10.

</details>

<details>
<summary>📝 Explanation</summary>

This is a system design problem that combines several data structures. The challenge is making five operations efficient: postTweet, getNewsFeed, follow, unfollow and the underlying data management.

**Data structures:**

- `tweets: dict[int, list[tuple[int, int]]]` - maps each user ID to their list of tweets, stored as `(timestamp, tweet_id)` pairs. Newest tweets are appended to the end.
- `following: dict[int, set[int]]` - maps each user ID to the set of user IDs they follow. Using a set makes follow/unfollow O(1) and prevents duplicate follows.
- A global timestamp counter that increments on every `postTweet` call, giving each tweet a unique ordering.

**Operations:**

- `postTweet(userId, tweetId)`: Append `(timestamp, tweetId)` to `tweets[userId]`. Increment timestamp. O(1).
- `follow(followerId, followeeId)`: Add followeeId to `following[followerId]`. O(1) set add.
- `unfollow(followerId, followeeId)`: Remove followeeId from `following[followerId]`. O(1) set discard.
- `getNewsFeed(userId)`: This is the interesting one. Collect tweets from the user and all followed users, then return the 10 most recent.

**News feed algorithm (K-way merge with a heap):**

The user follows K other users. Each user's tweet list is sorted by timestamp (oldest to newest). We need the 10 most recent tweets across all K+1 users (self + followed).

1. For each relevant user, grab their most recent tweet and push it onto a max-heap (negate the timestamp for Python's min-heap).
2. Pop the heap to get the most recent tweet overall. Add it to the result.
3. If that user has more tweets, push their next most recent tweet onto the heap.
4. Repeat until we have 10 tweets or the heap is empty.

This is the same K-way merge pattern from Merge K Sorted Lists (pattern 05, problem 23). The heap ensures we always pick the most recent tweet across all users without sorting everything from scratch.

**Time:** O(k log k) for getNewsFeed where k is the number of relevant users. The heap holds at most k entries, and we do at most 10 pop+push cycles. All other operations are O(1).
**Space:** O(total tweets + total follow edges).

</details>

<details>
<summary>💻 Code</summary>

See `p355_design_twitter.py` for the full implementation.

</details>

---

## Edge Cases

| Case | Scenario | Why It Matters |
|------|----------|----------------|
| Self follow | User follows themselves | Ignore it - they already see their own tweets |
| Unfollow non-followed | `unfollow(1, 2)` when 1 doesn't follow 2 | Should not error |
| Empty feed | New user with no tweets and no follows | Return empty list |
| More than 10 tweets | User has posted 15 tweets | Feed only returns 10 most recent |
| Multiple users merged | Following 3 users who all posted | Merge correctly by timestamp |

---

## Common Pitfalls

1. **Not including the user's own tweets in their feed** - The feed includes tweets from the user themselves, not just people they follow
2. **Following yourself** - Don't add self to the following set. The get_news_feed method should always include the user's own tweets separately.
3. **Heap direction** - Python's `heapq` is a min-heap. Negate timestamps to get max-heap behavior (most recent first).
4. **Merging all tweets instead of streaming** - Don't collect all tweets into one list and sort. Use the heap to lazily merge, stopping at 10.

---

## Interview Tips

**What to say:**
> "I need hash maps for tweets-per-user and follow relationships. The news feed is the interesting part - it's a merge-K-sorted-lists problem. Each user's tweets are already time-ordered, so I use a heap to merge them and stop after 10."

**This problem combines two patterns** - hash maps for storage and a heap for the merge. Interviewers are testing whether you can decompose a design problem into known algorithmic components.

**Follow-up: "How would you scale this?"**
→ Fan-out on write (pre-compute feeds when tweets are posted) vs fan-out on read (merge at read time, what we implemented). Fan-out on write is better for read-heavy systems (most users read more than they write). This is a classic system design discussion.

**What the interviewer evaluates at each stage:** Choosing the right data structures (dict of lists for tweets, dict of sets for follows) tests design sense. The K-way merge with a heap tests whether you can decompose a design problem into known algorithmic components. At principal level, the fan-out-on-write vs fan-out-on-read discussion is the real test - it shows you understand the system design trade-offs that matter at scale, not just the in-memory implementation.

---

## DE Application

This problem mirrors real data engineering challenges:
- Merging multiple sorted event streams (from different Kafka partitions, different data sources)
- Building activity feeds or audit logs from multiple sources
- The fan-out-on-write vs fan-out-on-read tradeoff appears in data pipeline design (pre-aggregate vs query-time aggregation)

The merge-K-sorted pattern shows up whenever you're combining partitioned, time-ordered data.

---

## At Scale

This is a system design problem disguised as a data structures problem. The in-memory approach works for the LeetCode constraints but breaks immediately at Twitter's actual scale (500M tweets/day). The real trade-off is fan-out-on-write (precompute each user's feed when a tweet is posted, like we do here with the merge) vs fan-out-on-read (compute the feed on demand). Fan-out-on-write uses more storage and write amplification but faster reads. Fan-out-on-read saves storage but every feed request is expensive. Hybrid approaches handle both: fan-out-on-write for normal users, fan-out-on-read for celebrities (whose tweets would fan out to millions). An interviewer using this problem at principal level will pivot to the system design trade-offs.

---

## Related Problems

- [23. Merge K Sorted Lists](https://leetcode.com/problems/merge-k-sorted-lists/) - The core algorithm used in getNewsFeed
- [146. LRU Cache](146_lru_cache.md) - Another "design a data structure" problem
- [380. Insert Delete GetRandom O(1)](380_insert_delete_random.md) - Combining data structures for different O(1) operations
