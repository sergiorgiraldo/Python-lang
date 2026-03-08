"""
DE Scenario: Heavy hitter (hot key) detection using Count-Min Sketch.

Real-world application: identifying hot partition keys that cause skew
in distributed systems. If one key gets 10% of all traffic, any
hash-partitioned system will bottleneck on that partition.

Run: uv run python -m patterns.11_probabilistic_structures.de_scenarios.heavy_hitters
"""

import sys
import random
sys.path.insert(0, "patterns/11_probabilistic_structures/problems")

from count_min_sketch import CountMinSketchWithHeavyHitters


def simulate_hot_key_detection(
    events: list[str],
    threshold: float = 0.01,
) -> dict:
    """Detect hot keys in a stream of partition keys."""
    hh = CountMinSketchWithHeavyHitters(width=2000, depth=5, top_k=50)

    for event in events:
        hh.add(event)

    detected = hh.heavy_hitters(threshold)

    return {
        "total_events": len(events),
        "threshold": threshold,
        "detected_hot_keys": [(k, v) for k, v in sorted(detected, key=lambda x: -x[1])],
        "memory_bytes": hh.cms.memory_bytes,
    }


if __name__ == "__main__":
    print("=== Heavy Hitter Detection ===\n")

    # Simulate key distribution with skew
    # 5 hot keys get 40% of traffic, 10K normal keys share 60%
    events = []
    hot_keys = [f"hot_key_{i}" for i in range(5)]
    normal_keys = [f"key_{i:05d}" for i in range(10000)]

    # Hot keys: 8% each (40% total)
    for key in hot_keys:
        events.extend([key] * 8000)

    # Normal keys: ~6 each (60% total)
    for key in normal_keys:
        events.extend([key] * random.randint(4, 8))

    random.shuffle(events)

    print(f"  Total events: {len(events):,}")
    print(f"  Hot keys: {len(hot_keys)}")
    print(f"  Normal keys: {len(normal_keys):,}")

    result = simulate_hot_key_detection(events, threshold=0.01)

    print(f"\n  Detected hot keys (>{result['threshold']:.0%} of traffic):")
    for key, count in result["detected_hot_keys"][:10]:
        pct = count / result["total_events"] * 100
        print(f"    {key}: ~{count:,} events ({pct:.1f}%)")

    print(f"\n  CMS memory: {result['memory_bytes']:,} bytes")
    print(f"  Exact tracking would need: ~{len(set(events)) * 70:,} bytes")
