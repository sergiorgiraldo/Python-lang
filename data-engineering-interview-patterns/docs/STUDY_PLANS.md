# Study Plans

Three preparation tracks based on your available time.
Each plan prioritizes problems by interview frequency and
builds skills progressively - earlier days cover fundamentals
that later days build on.

**How to use these plans:**
- Work through problems in order (each day builds on the previous)
- For each problem: read the .md first, try to solve it, then check the solution
- Run the tests to verify your understanding
- Read the DE Application and At Scale sections - these are what distinguish you
- Mark problems you struggled with and revisit them

---

## Track 1: One-Week Sprint (7 days)

**Target audience:** You have an interview next week. Focus on the highest-frequency problems and patterns.

**Philosophy:** Cover the top 25+ problems that appear most often. Skip edge cases and deep optimization. Know the patterns, be able to implement them and understand the DE applications.

### Day 1: Hash Maps + Basic SQL (~3 hours)

*Algorithmic (4 problems):*
- [Two Sum](../patterns/01_hash_map/problems/001_two_sum.md) - Easy
- [Contains Duplicate](../patterns/01_hash_map/problems/217_contains_duplicate.md) - Easy
- [Valid Anagram](../patterns/01_hash_map/problems/242_valid_anagram.md) - Easy
- [Group Anagrams](../patterns/01_hash_map/problems/049_group_anagrams.md) - Medium

*SQL (2 problems):*
- [Second Highest Salary](../sql/01_window_functions/problems/176_second_highest_salary.md) - Medium
- [Rank Scores](../sql/01_window_functions/problems/178_rank_scores.md) - Medium

*System Design (15 min):*
- Read [Communication Framework](../system_design/foundations/communication_framework.md)

### Day 2: Two Pointers + Binary Search (~3 hours)

*Algorithmic (4 problems):*
- [Merge Sorted Array](../patterns/02_two_pointers/problems/088_merge_sorted.md) - Easy
- [Two Sum II](../patterns/02_two_pointers/problems/167_two_sum_ii.md) - Medium
- [Binary Search](../patterns/03_binary_search/problems/704_binary_search.md) - Easy
- [Search in Rotated Sorted Array](../patterns/03_binary_search/problems/033_search_rotated.md) - Medium

*SQL (2 problems):*
- [Rising Temperature](../sql/01_window_functions/problems/197_rising_temperature.md) - Easy
- [Consecutive Numbers](../sql/01_window_functions/problems/180_consecutive_numbers.md) - Medium

*System Design (15 min):*
- Read [Tradeoff Framework](../system_design/foundations/tradeoff_framework.md)

### Day 3: Sliding Window + Heap (~3 hours)

*Algorithmic (3 problems):*
- [Longest Substring Without Repeating Characters](../patterns/04_sliding_window/problems/003_longest_substring.md) - Medium
- [Top K Frequent Elements](../patterns/01_hash_map/problems/347_top_k_frequent.md) - Medium
- [Find Median from Data Stream](../patterns/05_heap_priority_queue/problems/295_find_median_stream.md) - Hard

*SQL (2 problems):*
- [Department Highest Salary](../sql/01_window_functions/problems/184_department_highest_salary.md) - Medium
- [Department Top Three Salaries](../sql/01_window_functions/problems/185_department_top_three_salaries.md) - Hard

*System Design (15 min):*
- Read [Capacity Estimation](../system_design/foundations/capacity_estimation.md)

### Day 4: Graph + Intervals (~3.5 hours)

*Algorithmic (4 problems):*
- [Number of Islands](../patterns/06_graph_topological_sort/problems/200_number_of_islands.md) - Medium
- [Course Schedule](../patterns/06_graph_topological_sort/problems/207_course_schedule.md) - Medium
- [Merge Intervals](../patterns/07_intervals/problems/056_merge_intervals.md) - Medium
- [Meeting Rooms II](../patterns/07_intervals/problems/253_meeting_rooms_ii.md) - Medium

*SQL (2 problems):*
- [Combine Two Tables](../sql/02_joins/problems/175_combine_two_tables.md) - Easy
- [Customers Who Never Order](../sql/02_joins/problems/183_customers_who_never_order.md) - Easy

*System Design (20 min):*
- Read [Ingestion Patterns](../system_design/patterns/ingestion_patterns.md)

### Day 5: Stack + Trees + Design (~3.5 hours)

*Algorithmic (4 problems):*
- [Valid Parentheses](../patterns/08_stack/problems/020_valid_parentheses.md) - Easy
- [Daily Temperatures](../patterns/08_stack/problems/739_daily_temperatures.md) - Medium
- [Max Depth of Binary Tree](../patterns/10_recursion_trees/problems/104_max_depth.md) - Easy
- [LRU Cache](../patterns/01_hash_map/problems/146_lru_cache.md) - Medium

*SQL (2 problems):*
- [Duplicate Emails](../sql/03_aggregations/problems/182_duplicate_emails.md) - Easy
- [Game Play Analysis IV](../sql/01_window_functions/problems/550_game_play_analysis_iv.md) - Medium

*System Design (20 min):*
- Read [Data Modeling Patterns](../system_design/patterns/data_modeling_patterns.md)

### Day 6: SQL Deep Dive + System Design (~3.5 hours)

*SQL (3 problems):*
- [Human Traffic of Stadium](../sql/01_window_functions/problems/601_human_traffic_of_stadium.md) - Hard
- [Trips and Users](../sql/02_joins/problems/262_trips_and_users.md) - Hard
- [Delete Duplicate Emails](../sql/02_joins/problems/196_delete_duplicate_emails.md) - Easy

*DE Scenarios (2 scenarios):*
- [Dedup with ROW_NUMBER](../sql/01_window_functions/de_scenarios/dedup_with_row_number.md)
- [Sessionization](../sql/01_window_functions/de_scenarios/sessionization.md)

*dbt (15 min):*
- Review [stg_events](../sql/06_dbt_patterns/dbt_project/models/staging/stg_events.sql) to see how dedup looks in production dbt code

*System Design (40 min):*
- Read [Design an Event Pipeline](../system_design/walkthroughs/design_event_pipeline.md)
- Read [Design a Data Warehouse](../system_design/walkthroughs/design_data_warehouse.md)

### Day 7: Review + System Design Practice (~2.5 hours)

- Revisit 3-5 problems you struggled with
- Read [Design a Real-Time Dashboard](../system_design/walkthroughs/design_real_time_dashboard.md) (20 min)
- Review [Pattern Recognition Guide](PATTERN_RECOGNITION.md) (15 min)
- Review [Time Complexity Cheat Sheet](TIME_COMPLEXITY_CHEATSHEET.md) (10 min)
- Skim [Spark vs Python Cheatsheet](../spark/reference/spark_vs_python_cheatsheet.md) (10 min)
- Practice explaining one system design walkthrough out loud (20 min)

**Week total: ~22 hours, ~30 problems**

---

## Track 2: Two-Week Plan (14 days)

**Target audience:** You have 2 weeks. Cover all Common and Very Common problems. Include more SQL and system design depth.

**Philosophy:** Thorough coverage of common problems plus DE-specific depth. You will be well-prepared for standard rounds. Add system design practice in week 2.

### Week 1: Core Patterns

#### Day 1: Hash Map Fundamentals (~2.5 hours)

*Algorithmic (3 problems):*
- [Two Sum](../patterns/01_hash_map/problems/001_two_sum.md) - Easy
- [Contains Duplicate](../patterns/01_hash_map/problems/217_contains_duplicate.md) - Easy
- [Valid Anagram](../patterns/01_hash_map/problems/242_valid_anagram.md) - Easy

*SQL (1 problem):*
- [Second Highest Salary](../sql/01_window_functions/problems/176_second_highest_salary.md) - Medium

*System Design (15 min):*
- Read [Communication Framework](../system_design/foundations/communication_framework.md)

#### Day 2: Hash Map Applications (~2.5 hours)

*Algorithmic (3 problems):*
- [Group Anagrams](../patterns/01_hash_map/problems/049_group_anagrams.md) - Medium
- [Top K Frequent Elements](../patterns/01_hash_map/problems/347_top_k_frequent.md) - Medium
- [Subarray Sum Equals K](../patterns/01_hash_map/problems/560_subarray_sum_k.md) - Medium

*SQL (1 problem):*
- [Rank Scores](../sql/01_window_functions/problems/178_rank_scores.md) - Medium

#### Day 3: Two Pointers (~3 hours)

*Algorithmic (3 problems):*
- [Merge Sorted Array](../patterns/02_two_pointers/problems/088_merge_sorted.md) - Easy
- [3Sum](../patterns/02_two_pointers/problems/015_three_sum.md) - Medium
- [Container With Most Water](../patterns/02_two_pointers/problems/011_container_water.md) - Medium

*SQL (1 problem):*
- [Rising Temperature](../sql/01_window_functions/problems/197_rising_temperature.md) - Easy

*System Design (15 min):*
- Read [Tradeoff Framework](../system_design/foundations/tradeoff_framework.md)

#### Day 4: Binary Search (~2.5 hours)

*Algorithmic (3 problems):*
- [Binary Search](../patterns/03_binary_search/problems/704_binary_search.md) - Easy
- [Search in Rotated Sorted Array](../patterns/03_binary_search/problems/033_search_rotated.md) - Medium
- [Koko Eating Bananas](../patterns/03_binary_search/problems/875_koko_bananas.md) - Medium

*SQL (1 problem):*
- [Consecutive Numbers](../sql/01_window_functions/problems/180_consecutive_numbers.md) - Medium

*System Design (15 min):*
- Read [Capacity Estimation](../system_design/foundations/capacity_estimation.md)

#### Day 5: Sliding Window + Heap (~3 hours)

*Algorithmic (3 problems):*
- [Longest Substring Without Repeating Characters](../patterns/04_sliding_window/problems/003_longest_substring.md) - Medium
- [Sliding Window Maximum](../patterns/04_sliding_window/problems/239_sliding_window_max.md) - Hard
- [Find Median from Data Stream](../patterns/05_heap_priority_queue/problems/295_find_median_stream.md) - Hard

*SQL (2 problems):*
- [Department Highest Salary](../sql/01_window_functions/problems/184_department_highest_salary.md) - Medium
- [Combine Two Tables](../sql/02_joins/problems/175_combine_two_tables.md) - Easy

#### Day 6: Graph + Topological Sort (~3 hours)

*Algorithmic (3 problems):*
- [Number of Islands](../patterns/06_graph_topological_sort/problems/200_number_of_islands.md) - Medium
- [Course Schedule](../patterns/06_graph_topological_sort/problems/207_course_schedule.md) - Medium
- [Course Schedule II](../patterns/06_graph_topological_sort/problems/210_course_schedule_ii.md) - Medium

*SQL (2 problems):*
- [Customers Who Never Order](../sql/02_joins/problems/183_customers_who_never_order.md) - Easy
- [Duplicate Emails](../sql/03_aggregations/problems/182_duplicate_emails.md) - Easy

*System Design (20 min):*
- Read [Ingestion Patterns](../system_design/patterns/ingestion_patterns.md)

#### Day 7: Intervals + Stack + Trees (~2.5 hours)

*Algorithmic (3 problems):*
- [Merge Intervals](../patterns/07_intervals/problems/056_merge_intervals.md) - Medium
- [Valid Parentheses](../patterns/08_stack/problems/020_valid_parentheses.md) - Easy
- [Max Depth of Binary Tree](../patterns/10_recursion_trees/problems/104_max_depth.md) - Easy

*SQL (1 problem):*
- [Department Top Three Salaries](../sql/01_window_functions/problems/185_department_top_three_salaries.md) - Hard

*System Design (20 min):*
- Read [Data Modeling Patterns](../system_design/patterns/data_modeling_patterns.md)

### Week 2: Depth + Review

#### Day 8: Streaming Patterns (~3 hours)

*Algorithmic (3 problems):*
- [Longest Consecutive Sequence](../patterns/01_hash_map/problems/128_longest_consecutive.md) - Medium
- [Meeting Rooms II](../patterns/07_intervals/problems/253_meeting_rooms_ii.md) - Medium
- [Daily Temperatures](../patterns/08_stack/problems/739_daily_temperatures.md) - Medium

*SQL (2 problems):*
- [Nth Highest Salary](../sql/01_window_functions/problems/177_nth_highest_salary.md) - Medium
- [Game Play Analysis IV](../sql/01_window_functions/problems/550_game_play_analysis_iv.md) - Medium

#### Day 9: Design + Tree Structures (~3 hours)

*Algorithmic (3 problems):*
- [LRU Cache](../patterns/01_hash_map/problems/146_lru_cache.md) - Medium
- [Serialize and Deserialize Binary Tree](../patterns/10_recursion_trees/problems/297_serialize_deserialize.md) - Hard
- [Max Depth of Binary Tree review + Subtree](../patterns/10_recursion_trees/problems/104_max_depth.md) - Easy

*SQL (2 problems):*
- [Employees Earning More Than Their Managers](../sql/02_joins/problems/181_employees_earning_more.md) - Easy
- [Delete Duplicate Emails](../sql/02_joins/problems/196_delete_duplicate_emails.md) - Easy

*System Design (20 min):*
- Read [Pipeline Architecture](../system_design/patterns/pipeline_architecture.md)

#### Day 10: Probabilistic Structures (~3 hours)

*Algorithmic (3 problems):*
- [Bloom Filter](../patterns/11_probabilistic_structures/problems/bloom_filter.md) - Medium
- [HyperLogLog](../patterns/11_probabilistic_structures/problems/hyperloglog.md) - Medium
- [Count-Min Sketch](../patterns/11_probabilistic_structures/problems/count_min_sketch.md) - Medium

*SQL (2 problems):*
- [Human Traffic of Stadium](../sql/01_window_functions/problems/601_human_traffic_of_stadium.md) - Hard
- [Managers with at Least 5 Reports](../sql/02_joins/problems/570_managers_with_5_reports.md) - Medium

#### Day 11: SQL DE Scenarios I (~3 hours)

*SQL (2 problems):*
- [Trips and Users](../sql/02_joins/problems/262_trips_and_users.md) - Hard
- [Employees Earning More review](../sql/02_joins/problems/181_employees_earning_more.md) - Easy

*DE Scenarios (3 scenarios):*
- [Dedup with ROW_NUMBER](../sql/01_window_functions/de_scenarios/dedup_with_row_number.md)
- [Sessionization](../sql/01_window_functions/de_scenarios/sessionization.md)
- [Change Detection](../sql/01_window_functions/de_scenarios/change_detection.md)

*dbt Patterns (30 min):*
- Review [staging models](../sql/06_dbt_patterns/dbt_project/models/staging/) to see how dedup and cleaning look in production
- Review [int_deduped_events](../sql/06_dbt_patterns/dbt_project/models/intermediate/int_deduped_events.sql) for sessionization in dbt
- Skim [interview_guide](../sql/06_dbt_patterns/interview_guide.md) for common dbt interview questions

*System Design (20 min):*
- Read [Data Quality Patterns](../system_design/patterns/data_quality_patterns.md)

#### Day 12: SQL DE Scenarios II + System Design (~2.5 hours)

*DE Scenarios (4 scenarios):*
- [Running Totals](../sql/01_window_functions/de_scenarios/running_totals.md)
- [Moving Averages](../sql/01_window_functions/de_scenarios/moving_averages.md)
- [MERGE / Upsert Patterns](../sql/02_joins/de_scenarios/merge_upsert.md)
- [Incremental Load Detection](../sql/02_joins/de_scenarios/incremental_load.md)

*System Design (20 min):*
- Read [Scale and Performance](../system_design/patterns/scale_and_performance.md)

#### Day 13: System Design Walkthroughs + PySpark (~3 hours)

- Read [Design an Event Pipeline](../system_design/walkthroughs/design_event_pipeline.md) (30 min)
- Read [Design a Data Warehouse](../system_design/walkthroughs/design_data_warehouse.md) (30 min)
- Review [Spark vs Python Cheatsheet](../spark/reference/spark_vs_python_cheatsheet.md) (15 min)
- Read [spark/01_joins/broadcast_join.py](../spark/01_joins/broadcast_join.py) as a worked example (15 min)
- Review [Pattern Recognition Guide](PATTERN_RECOGNITION.md) (15 min)
- Review [Time Complexity Cheat Sheet](TIME_COMPLEXITY_CHEATSHEET.md) (10 min)
- Practice explaining one walkthrough out loud (20 min)

#### Day 14: Review + Final Prep (~2.5 hours)

- Revisit 3-5 problems you struggled with
- Read [Design a Real-Time Dashboard](../system_design/walkthroughs/design_real_time_dashboard.md) (20 min)
- Review [Interview Strategy Guide](INTERVIEW_STRATEGY.md) (15 min)
- Practice explaining solutions out loud (30 min)

**Two-week total: ~38 hours, ~46 problems + 7 DE scenarios + system design**

---

## Track 3: One-Month Comprehensive (30 days)

**Target audience:** You are starting a job search. Systematic coverage of everything in the repo.

**Philosophy:** Build deep understanding, not just pattern matching. Cover all problems, study the DE scenarios and internalize the system design frameworks. Practice explaining your solutions.

### Week 1: Core Algorithm Patterns (Days 1-7)

One core pattern per day. Focus on Very Common and Common problems first.

#### Day 1: Hash Maps - Fundamentals (~2.5 hours)

- [Two Sum](../patterns/01_hash_map/problems/001_two_sum.md) - Easy
- [Contains Duplicate](../patterns/01_hash_map/problems/217_contains_duplicate.md) - Easy
- [Valid Anagram](../patterns/01_hash_map/problems/242_valid_anagram.md) - Easy
- [Group Anagrams](../patterns/01_hash_map/problems/049_group_anagrams.md) - Medium

*System Design (15 min):*
- Read [Communication Framework](../system_design/foundations/communication_framework.md)

#### Day 2: Hash Maps - Applications (~2.5 hours)

- [Top K Frequent Elements](../patterns/01_hash_map/problems/347_top_k_frequent.md) - Medium
- [Subarray Sum Equals K](../patterns/01_hash_map/problems/560_subarray_sum_k.md) - Medium
- [Longest Consecutive Sequence](../patterns/01_hash_map/problems/128_longest_consecutive.md) - Medium

*System Design (15 min):*
- Read [Tradeoff Framework](../system_design/foundations/tradeoff_framework.md)

*Benchmark:*
- Run [Hash Map vs Nested Loop](../benchmarks/hash_map_vs_nested_loop.py) to see O(n) vs O(n^2)

#### Day 3: Two Pointers (~2.5 hours)

- [Merge Sorted Array](../patterns/02_two_pointers/problems/088_merge_sorted.md) - Easy
- [3Sum](../patterns/02_two_pointers/problems/015_three_sum.md) - Medium
- [Container With Most Water](../patterns/02_two_pointers/problems/011_container_water.md) - Medium

*Benchmark:*
- Run [Two Pointer Merge vs Sort](../benchmarks/two_pointer_merge_vs_sort.py)

#### Day 4: Binary Search (~2.5 hours)

- [Binary Search](../patterns/03_binary_search/problems/704_binary_search.md) - Easy
- [Search in Rotated Sorted Array](../patterns/03_binary_search/problems/033_search_rotated.md) - Medium
- [Koko Eating Bananas](../patterns/03_binary_search/problems/875_koko_bananas.md) - Medium

*System Design (15 min):*
- Read [Capacity Estimation](../system_design/foundations/capacity_estimation.md)

*Benchmark:*
- Run [Binary Search vs Linear](../benchmarks/binary_search_vs_linear.py)

#### Day 5: Sliding Window (~2.5 hours)

- [Longest Substring Without Repeating Characters](../patterns/04_sliding_window/problems/003_longest_substring.md) - Medium
- [Sliding Window Maximum](../patterns/04_sliding_window/problems/239_sliding_window_max.md) - Hard
- [Maximum Average Subarray](../patterns/04_sliding_window/problems/643_max_average_subarray.md) - Easy

*Benchmark:*
- Run [Sliding Window vs Recompute](../benchmarks/sliding_window_vs_recompute.py)

#### Day 6: Heap and Priority Queue (~2.5 hours)

- [Find Median from Data Stream](../patterns/05_heap_priority_queue/problems/295_find_median_stream.md) - Hard
- [Kth Largest Element in an Array](../patterns/05_heap_priority_queue/problems/215_kth_largest_array.md) - Medium
- [Kth Largest Element in a Stream](../patterns/05_heap_priority_queue/problems/703_kth_largest_stream.md) - Easy

*Benchmark:*
- Run [Heap vs Sort](../benchmarks/heap_vs_sort.py) and [Heap vs Sort Top-K](../benchmarks/heap_vs_sort_topk.py)

#### Day 7: Graph and Topological Sort (~2.5 hours)

- [Number of Islands](../patterns/06_graph_topological_sort/problems/200_number_of_islands.md) - Medium
- [Course Schedule](../patterns/06_graph_topological_sort/problems/207_course_schedule.md) - Medium
- [Course Schedule II](../patterns/06_graph_topological_sort/problems/210_course_schedule_ii.md) - Medium

*Benchmark:*
- Run [Graph Topological Sort](../benchmarks/graph_topo_sort.py)

**Week 1 total: 22 problems, 3 system design foundations, 8 benchmarks**

### Week 2: Remaining Patterns + SQL Start (Days 8-14)

Cover the remaining five pattern categories and begin the SQL section.

#### Day 8: Intervals (~2.5 hours)

- [Merge Intervals](../patterns/07_intervals/problems/056_merge_intervals.md) - Medium
- [Meeting Rooms II](../patterns/07_intervals/problems/253_meeting_rooms_ii.md) - Medium
- [Insert Interval](../patterns/07_intervals/problems/057_insert_interval.md) - Medium

*System Design (20 min):*
- Read [Ingestion Patterns](../system_design/patterns/ingestion_patterns.md)

*Benchmark:*
- Run [Interval Merge](../benchmarks/interval_merge.py)

#### Day 9: Stack (~2.5 hours)

- [Valid Parentheses](../patterns/08_stack/problems/020_valid_parentheses.md) - Easy
- [Daily Temperatures](../patterns/08_stack/problems/739_daily_temperatures.md) - Medium
- [Min Stack](../patterns/08_stack/problems/155_min_stack.md) - Medium
- [Evaluate Reverse Polish Notation](../patterns/08_stack/problems/150_eval_rpn.md) - Medium

*SQL (1 problem):*
- [Second Highest Salary](../sql/01_window_functions/problems/176_second_highest_salary.md) - Medium

#### Day 10: Trees and Recursion (~3 hours)

- [Max Depth of Binary Tree](../patterns/10_recursion_trees/problems/104_max_depth.md) - Easy
- [Invert Binary Tree](../patterns/10_recursion_trees/problems/226_invert_tree.md) - Easy
- [Serialize and Deserialize Binary Tree](../patterns/10_recursion_trees/problems/297_serialize_deserialize.md) - Hard
- [Subtree of Another Tree](../patterns/10_recursion_trees/problems/572_subtree.md) - Easy

*SQL (1 problem):*
- [Rank Scores](../sql/01_window_functions/problems/178_rank_scores.md) - Medium

#### Day 11: Probabilistic Structures (~3 hours)

- [Bloom Filter](../patterns/11_probabilistic_structures/problems/bloom_filter.md) - Medium
- [HyperLogLog](../patterns/11_probabilistic_structures/problems/hyperloglog.md) - Medium
- [Count-Min Sketch](../patterns/11_probabilistic_structures/problems/count_min_sketch.md) - Medium

*SQL (2 problems):*
- [Rising Temperature](../sql/01_window_functions/problems/197_rising_temperature.md) - Easy
- [Consecutive Numbers](../sql/01_window_functions/problems/180_consecutive_numbers.md) - Medium

*System Design (20 min):*
- Read [Data Modeling Patterns](../system_design/patterns/data_modeling_patterns.md)

#### Day 12: String Parsing (~3 hours)

- [Encode and Decode Strings](../patterns/09_string_parsing/problems/271_encode_decode_strings.md) - Medium
- [Decode String](../patterns/09_string_parsing/problems/394_decode_string.md) - Medium
- [Validate IP Address](../patterns/09_string_parsing/problems/468_validate_ip_address.md) - Medium
- [Remove Comments](../patterns/09_string_parsing/problems/722_remove_comments.md) - Medium

*SQL (1 problem):*
- [Department Highest Salary](../sql/01_window_functions/problems/184_department_highest_salary.md) - Medium

#### Day 13: Combined Patterns (~3 hours)

- [Task Scheduler](../patterns/12_combined_patterns/problems/621_task_scheduler.md) - Medium
- [Top K Frequent Words](../patterns/12_combined_patterns/problems/692_top_k_words.md) - Medium
- [Cheapest Flights Within K Stops](../patterns/12_combined_patterns/problems/787_cheapest_flights.md) - Medium
- [Maximum Frequency Stack](../patterns/12_combined_patterns/problems/895_max_freq_stack.md) - Hard

*SQL (1 problem):*
- [Combine Two Tables](../sql/02_joins/problems/175_combine_two_tables.md) - Easy

*System Design (20 min):*
- Read [Pipeline Architecture](../system_design/patterns/pipeline_architecture.md)

#### Day 14: Hash Map Advanced + SQL Joins (~3 hours)

- [LRU Cache](../patterns/01_hash_map/problems/146_lru_cache.md) - Medium
- [Design Twitter](../patterns/01_hash_map/problems/355_design_twitter.md) - Medium
- [Insert Delete GetRandom O(1)](../patterns/01_hash_map/problems/380_insert_delete_random.md) - Medium

*SQL (2 problems):*
- [Customers Who Never Order](../sql/02_joins/problems/183_customers_who_never_order.md) - Easy
- [Duplicate Emails](../sql/03_aggregations/problems/182_duplicate_emails.md) - Easy

**Week 2 total: 24 algorithmic + 8 SQL = 32 problems, 3 system design readings**

### Week 3: Remaining Algorithms + SQL Deep Dive (Days 15-21)

Complete all remaining algorithmic problems while working through the SQL section.

#### Day 15: Two Pointers Deep Dive (~3 hours)

- [Remove Duplicates from Sorted Array](../patterns/02_two_pointers/problems/026_remove_duplicates.md) - Easy
- [Trapping Rain Water](../patterns/02_two_pointers/problems/042_trapping_rain_water.md) - Hard
- [Two Sum II](../patterns/02_two_pointers/problems/167_two_sum_ii.md) - Medium
- [Sort Colors](../patterns/02_two_pointers/problems/075_sort_colors.md) - Medium

*SQL (2 problems):*
- [Department Top Three Salaries](../sql/01_window_functions/problems/185_department_top_three_salaries.md) - Hard
- [Nth Highest Salary](../sql/01_window_functions/problems/177_nth_highest_salary.md) - Medium

*System Design (20 min):*
- Read [Data Quality Patterns](../system_design/patterns/data_quality_patterns.md)

#### Day 16: Array Fundamentals Catch-up (~3 hours)

- [Move Zeroes](../patterns/02_two_pointers/problems/283_move_zeroes.md) - Easy
- [Squares of a Sorted Array](../patterns/02_two_pointers/problems/977_squares_sorted.md) - Easy
- [Search Insert Position](../patterns/03_binary_search/problems/035_search_insert.md) - Easy
- [Search a 2D Matrix](../patterns/03_binary_search/problems/074_search_2d_matrix.md) - Medium

*SQL (2 problems):*
- [Employees Earning More Than Their Managers](../sql/02_joins/problems/181_employees_earning_more.md) - Easy
- [Delete Duplicate Emails](../sql/02_joins/problems/196_delete_duplicate_emails.md) - Easy

#### Day 17: Binary Search Variations (~3 hours)

- [Find Minimum in Rotated Sorted Array](../patterns/03_binary_search/problems/153_find_min_rotated.md) - Medium
- [Find Peak Element](../patterns/03_binary_search/problems/162_find_peak.md) - Medium
- [Time Based Key-Value Store](../patterns/03_binary_search/problems/981_time_map.md) - Medium

*SQL (2 problems):*
- [Trips and Users](../sql/02_joins/problems/262_trips_and_users.md) - Hard
- [Game Play Analysis IV](../sql/01_window_functions/problems/550_game_play_analysis_iv.md) - Medium

*System Design (20 min):*
- Read [Scale and Performance](../system_design/patterns/scale_and_performance.md)

#### Day 18: Sliding Window Deep Dive (~3 hours)

- [Minimum Window Substring](../patterns/04_sliding_window/problems/076_min_window_substring.md) - Hard
- [Contains Duplicate II](../patterns/04_sliding_window/problems/219_contains_duplicate_ii.md) - Easy
- [Longest Repeating Character Replacement](../patterns/04_sliding_window/problems/424_longest_repeating_char.md) - Medium
- [Find All Anagrams in a String](../patterns/04_sliding_window/problems/438_find_all_anagrams.md) - Medium

*SQL (2 problems):*
- [Human Traffic of Stadium](../sql/01_window_functions/problems/601_human_traffic_of_stadium.md) - Hard
- [Managers with at Least 5 Reports](../sql/02_joins/problems/570_managers_with_5_reports.md) - Medium

#### Day 19: Window Patterns + Heap (~3 hours)

- [Permutation in String](../patterns/04_sliding_window/problems/567_permutation_in_string.md) - Medium
- [Merge k Sorted Lists](../patterns/05_heap_priority_queue/problems/023_merge_k_sorted.md) - Hard
- [Last Stone Weight](../patterns/05_heap_priority_queue/problems/1046_last_stone_weight.md) - Easy
- [Reorganize String](../patterns/05_heap_priority_queue/problems/767_reorganize_string.md) - Medium

*SQL (2 problems):*
- [Game Play Analysis I](../sql/03_aggregations/problems/511_game_play_analysis_i.md) - Easy
- [Count Students per Department](../sql/02_joins/problems/580_count_students_per_dept.md) - Easy

#### Day 20: Graph + Intervals Remaining (~3 hours)

- [Clone Graph](../patterns/06_graph_topological_sort/problems/133_clone_graph.md) - Medium
- [Alien Dictionary](../patterns/06_graph_topological_sort/problems/269_alien_dictionary.md) - Hard
- [Number of Provinces](../patterns/06_graph_topological_sort/problems/547_number_of_provinces.md) - Medium
- [Network Delay Time](../patterns/06_graph_topological_sort/problems/743_network_delay_time.md) - Medium

*SQL (2 problems):*
- [Winning Candidate](../sql/03_aggregations/problems/574_winning_candidate.md) - Medium
- [Friend Requests II](../sql/02_joins/problems/602_friend_requests_most_friends.md) - Medium

#### Day 21: Final Patterns Wrap-up (~3 hours)

- [Meeting Rooms](../patterns/07_intervals/problems/252_meeting_rooms.md) - Easy
- [Non-overlapping Intervals](../patterns/07_intervals/problems/435_non_overlapping.md) - Medium
- [Interval List Intersections](../patterns/07_intervals/problems/986_interval_intersections.md) - Medium
- [Largest Rectangle in Histogram](../patterns/08_stack/problems/084_largest_rectangle.md) - Hard
- [Car Fleet](../patterns/08_stack/problems/853_car_fleet.md) - Medium
- [Lowest Common Ancestor](../patterns/10_recursion_trees/problems/236_lca.md) - Medium

*SQL (2 problems):*
- [Investments in 2016](../sql/03_aggregations/problems/585_investments_in_2016.md) - Medium
- [Average Salary](../sql/03_aggregations/problems/615_average_salary.md) - Hard

*dbt Patterns (~1.5 hours):*
- Read [dbt Patterns README](../sql/06_dbt_patterns/README.md) (10 min)
- Review all [staging models](../sql/06_dbt_patterns/dbt_project/models/staging/) (15 min)
- Review all [intermediate models](../sql/06_dbt_patterns/dbt_project/models/intermediate/) (20 min)
- Review all [mart models](../sql/06_dbt_patterns/dbt_project/models/marts/) (15 min)
- Read [patterns_mapping](../sql/06_dbt_patterns/patterns_mapping.md) to connect dbt models to SQL patterns (10 min)
- Read [interview_guide](../sql/06_dbt_patterns/interview_guide.md) for dbt-specific interview prep (20 min)

**Week 3 total: 30 algorithmic + 14 SQL = 44 problems, 2 system design readings, dbt patterns**

### Week 4: SQL Advanced + DE Scenarios + System Design (Days 22-28)

Deep dive into DE-specific SQL patterns, scenarios and system design.

#### Day 22: SQL Recursive CTEs + DE Scenarios (~3 hours)

*SQL (4 problems):*
- [Median Employee Salary](../sql/04_recursive_ctes/problems/569_median_employee_salary.md) - Hard
- [Median Given Frequency](../sql/04_recursive_ctes/problems/571_median_given_frequency.md) - Hard
- [Cumulative Salary](../sql/04_recursive_ctes/problems/579_cumulative_salary.md) - Hard
- [Students Report](../sql/04_recursive_ctes/problems/618_students_report.md) - Hard

*DE Scenarios (2 scenarios):*
- [Dedup with ROW_NUMBER](../sql/01_window_functions/de_scenarios/dedup_with_row_number.md)
- [Sessionization](../sql/01_window_functions/de_scenarios/sessionization.md)

#### Day 23: Window Function DE Scenarios + SQL Patterns (~2.5 hours)

*DE Scenarios (3 scenarios):*
- [Change Detection](../sql/01_window_functions/de_scenarios/change_detection.md)
- [Running Totals](../sql/01_window_functions/de_scenarios/running_totals.md)
- [Moving Averages](../sql/01_window_functions/de_scenarios/moving_averages.md)

*SQL Advanced Patterns:*
- Read [GROUPING SETS, ROLLUP and CUBE](../sql/05_optimization_and_production/advanced_patterns/grouping_sets.md)
- Read [QUALIFY Clause](../sql/05_optimization_and_production/advanced_patterns/qualify_clause.md)

#### Day 24: Join DE Scenarios + SQL Patterns (~2.5 hours)

*DE Scenarios (4 scenarios):*
- [Anti-Joins for Finding Gaps](../sql/02_joins/de_scenarios/anti_joins.md)
- [Incremental Load Detection](../sql/02_joins/de_scenarios/incremental_load.md)
- [MERGE / Upsert Patterns](../sql/02_joins/de_scenarios/merge_upsert.md)
- [Self-Joins for Hierarchies](../sql/02_joins/de_scenarios/self_joins_hierarchies.md)

*SQL Advanced Patterns:*
- Read [LATERAL JOIN](../sql/05_optimization_and_production/advanced_patterns/lateral_join.md)
- Read [Semi-Structured Data](../sql/05_optimization_and_production/advanced_patterns/semi_structured_data.md)

#### Day 25: PySpark Patterns (~3 hours)

*PySpark (study + run tests):*
- Read [Spark README](../spark/README.md) for overview (10 min)
- Work through [broadcast_join.py](../spark/01_joins/broadcast_join.py) and [shuffle_join.py](../spark/01_joins/shuffle_join.py) (30 min)
- Work through [ranking_and_dedup.py](../spark/03_window_functions/ranking_and_dedup.py) and [sessionization.py](../spark/03_window_functions/sessionization.py) (30 min)
- Work through [partition_strategies.py](../spark/05_partitioning/partition_strategies.py) and [explain_plans.py](../spark/05_partitioning/explain_plans.py) (30 min)
- Read [Common Interview Questions](../spark/reference/common_interview_questions.md) (20 min)
- Run `uv run pytest spark/ -v` to see all tests pass (5 min)

#### Day 26: Aggregation + CTE DE Scenarios + Remaining PySpark (~3 hours)

*DE Scenarios (6 scenarios):*
- [Conditional Aggregation](../sql/03_aggregations/de_scenarios/conditional_aggregation.md)
- [Gap Detection](../sql/03_aggregations/de_scenarios/gap_detection.md)
- [Pivot Patterns](../sql/03_aggregations/de_scenarios/pivot_patterns.md)
- [Approximate Counting](../sql/03_aggregations/de_scenarios/approximate_counting.md)
- [Bill of Materials](../sql/04_recursive_ctes/de_scenarios/bill_of_materials.md)
- [Graph Traversal in SQL](../sql/04_recursive_ctes/de_scenarios/graph_traversal.md)

*PySpark (remaining files):*
- Work through [skew_handling.py](../spark/01_joins/skew_handling.py), [group_by_patterns.py](../spark/04_aggregations/group_by_patterns.py) and [structured_streaming_basics.py](../spark/06_streaming/structured_streaming_basics.py) (30 min)

#### Day 27: Remaining DE Scenarios + SQL Production (~3 hours)

*DE Scenarios (5 scenarios):*
- [Hierarchy Traversal](../sql/04_recursive_ctes/de_scenarios/hierarchy_traversal.md)
- [Path Enumeration](../sql/04_recursive_ctes/de_scenarios/path_enumeration.md)
- [Materialized Views](../sql/05_optimization_and_production/de_scenarios/materialized_views.md)
- [Partition Strategy](../sql/05_optimization_and_production/de_scenarios/partition_strategy.md)
- [Query Optimization](../sql/05_optimization_and_production/de_scenarios/query_optimization.md)

*SQL Reference:*
- Read [SQL Anti-Patterns](../sql/05_optimization_and_production/reference/anti_patterns.md)
- Read [EXPLAIN Plan Analysis](../sql/05_optimization_and_production/reference/explain_plans.md)
- Read [Cost-Aware Query Design](../sql/05_optimization_and_production/reference/cost_aware_queries.md)
- Read [SQL Dialect Comparison](../sql/05_optimization_and_production/reference/dialect_comparison.md)

#### Day 28: System Design Walkthroughs I (~3 hours)

- Read [Design an Event Pipeline](../system_design/walkthroughs/design_event_pipeline.md) (30 min)
- Read [Design a Data Warehouse](../system_design/walkthroughs/design_data_warehouse.md) (30 min)
- Read [Throughput and Latency Reference](../system_design/reference/throughput_numbers.md) (15 min)
- Read [Technology Decision Matrix](../system_design/reference/technology_decision_matrix.md) (15 min)
- Practice explaining the event pipeline design out loud (20 min)

#### Day 29: System Design Walkthroughs II (~3 hours)

- Read [Design a Real-Time Dashboard](../system_design/walkthroughs/design_real_time_dashboard.md) (30 min)
- Read [Design a Data Lake](../system_design/walkthroughs/design_data_lake.md) (30 min)
- Read [Design an ML Feature Store](../system_design/walkthroughs/design_ml_feature_store.md) (30 min)
- Read [Cost Models Reference](../system_design/reference/cost_models.md) (15 min)
- Practice explaining the data warehouse design out loud (20 min)

**Week 4 total: 4 SQL problems, 20 DE scenarios, PySpark section, all system design docs**

### Days 30-31: Final Review

#### Day 30: Review + Pattern Recognition (~3 hours)

- Revisit 5-8 problems you found most challenging
- Review [Pattern Recognition Guide](PATTERN_RECOGNITION.md) (15 min)
- Review [Time Complexity Cheat Sheet](TIME_COMPLEXITY_CHEATSHEET.md) (15 min)
- Re-run any benchmarks that surprised you (see [Benchmarks README](../benchmarks/README.md))

#### Day 31: Mock Interview + Final Prep (~3 hours)

- Read [Mock Interviews Guide](../mock_interviews/README.md) (10 min)
- Review [Interview Strategy Guide](INTERVIEW_STRATEGY.md) (15 min)
- Review [Glossary](GLOSSARY.md) (10 min)
- Practice a full mock interview: 1 coding problem (25 min) + 1 SQL problem (20 min) + 1 system design (45 min)
- Review your notes on weak areas one final time

**Month total: ~83 hours, 102 problems + 20 DE scenarios + PySpark patterns + all system design docs**

---

## Tips

### How to maximize study time

- Always time yourself (set a 25-minute timer for each problem)
- If stuck after 10 minutes, read the Thought Process section then try again
- After solving, always read the At Scale and DE Application sections
- For SQL: write the query before looking at the solution then compare approaches
- For system design: practice the 45-minute walkthrough format out loud at least twice
- Run the [benchmarks](../benchmarks/) scripts to internalize why complexity matters

### What to focus on by role level

- **Mid-level:** focus on coding + SQL, light system design
- **Senior:** balanced across all three sections
- **Principal/Staff:** heavy system design, moderate coding + SQL
- **All levels:** DE-specific applications and At Scale discussions
