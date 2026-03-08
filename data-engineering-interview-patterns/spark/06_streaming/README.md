# Streaming

## Pattern Connection

Maps to [`patterns/04_sliding_window/`](../../patterns/04_sliding_window/README.md)
(processing elements as they arrive) and
[`system_design/walkthroughs/design_event_pipeline`](../../system_design/walkthroughs/design_event_pipeline.md)
(real-time event processing).

The sliding window pattern in Python processes a fixed-size window over a sequence.
Structured Streaming extends this to unbounded data: new rows arrive continuously
and Spark processes them incrementally using tumbling, sliding or session windows.

## Key Concepts

**Structured Streaming model:** treats a stream as an unbounded table. New data
arrives as new rows. Queries run incrementally, processing only new rows each
micro-batch.

**Window types:**
- Tumbling: non-overlapping, fixed-size (`window("ts", "1 minute")`)
- Sliding: overlapping, fixed-size with slide interval (`window("ts", "1 minute", "30 seconds")`)
- Session: gap-based, variable-size (`session_window("ts", "10 minutes")`)

**Watermarks:** tell Spark how late data can arrive. Events older than the watermark
are dropped. Without a watermark, Spark must keep all state forever (memory grows
unbounded).

**Output modes:**
- Append: only new rows (after watermark closes a window)
- Complete: full result table each trigger (only for aggregations)
- Update: only changed rows each trigger

**Testing approach:** these files use the "rate" source (generates rows per second)
and "memory" sink (stores results in an in-memory table). This avoids external
dependencies like Kafka while still testing real streaming behavior.

## Interview Context

Streaming questions test whether you understand:
- The difference between batch and streaming execution
- How watermarks prevent unbounded state growth
- When to use each window type and output mode
- How late data is handled

## Files

| File | Description |
|---|---|
| `structured_streaming_basics.py` | Rate source, memory sink, watermarks, output modes |
| `window_aggregations.py` | Tumbling vs sliding windows, streaming aggregation patterns |
