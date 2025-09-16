#!/usr/bin/env python3

from datetime import datetime
from typing import List, Tuple

def parse_timestamp(timestamp_str: str) -> datetime:
    return datetime.strptime(timestamp_str, '%Y-%m-%d, %H:%M:%S')

def merge_overlapping_intervals(intervals: List[Tuple[datetime, datetime]]) -> List[Tuple[datetime, datetime]]:
    if not intervals:
        return []
    
    sorted_intervals = sorted(intervals, key=lambda x: x[0])
    merged = [sorted_intervals[0]]
    
    for current_start, current_end in sorted_intervals[1:]:
        last_start, last_end = merged[-1]
        
        if current_start <= last_end:
            merged[-1] = (last_start, max(last_end, current_end))
        else:
            merged.append((current_start, current_end))
    
    return merged

def calculate_total_duration(timestamp_pairs: List[Tuple[str, str]]) -> dict:
    intervals = []
    for start_str, end_str in timestamp_pairs:
        try:
            start_time = parse_timestamp(start_str)
            end_time = parse_timestamp(end_str)
            
            intervals.append((start_time, end_time))
        except ValueError as e:
            raise (f"Error parsing timestamps '{start_str}', '{end_str}': {e}")
    
    merged_intervals = merge_overlapping_intervals(intervals)
    
    total_seconds = 0
    for start, end in merged_intervals:
        duration = end - start
        total_seconds += duration.total_seconds()
        
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)
    formatted_duration = f"{hours}:{minutes:02d}:{seconds:02d}"
    
    return {
        'formatted_duration': formatted_duration,
        'merged_intervals_count': len(merged_intervals),
        'original_intervals_count': len(intervals)
    }

def print_results(result: dict, timestamp_pairs: List[Tuple[str, str]]):
    print(f"Original time periods: {result['original_intervals_count']}")
    print(f"After merging overlaps: {result['merged_intervals_count']}")
    print()
    
    print("Total Duration:")
    print(f"  - {result['formatted_duration']} (HH:MM:SS)")

def main():
    my_periods = [
("2025-09-11, 17:49:20","2025-09-11, 20:23:46"),    
    ]
    result = calculate_total_duration(my_periods)
    print_results(result, my_periods)

if __name__ == "__main__":
    main()

