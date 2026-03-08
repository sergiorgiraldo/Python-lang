# Communication Framework for System Design Interviews

Knowing the right answer is not enough. You have to communicate it clearly in
a structured, time-boxed format. The interviewer is evaluating your thought
process as much as your technical knowledge.

Two candidates with identical technical knowledge can get very different scores
based on how they structure and communicate their thinking. This document gives
you the structure.

## The 45-Minute Structure

Time management is the most underrated skill in system design interviews.
Running out of time before discussing scaling or failure modes signals poor
planning. Use this breakdown as your default pacing guide.

### Minutes 0-5: Clarify Requirements and Scope

Do not start drawing. Start asking.

- Repeat the problem back in your own words to confirm understanding
- Ask 3-5 clarifying questions (see the question list below)
- Establish functional requirements (what the system must do)
- Establish non-functional requirements (latency, throughput, cost, SLAs)
- State explicit assumptions: "I will assume X unless you would like me to
  consider Y"

This phase sets the constraints that drive every design decision. Skipping it
means you are designing blind.

### Minutes 5-10: High-Level Design

Draw the skeleton. 3-5 major components connected by data flow arrows.

- Name specific technologies: "Kafka for ingestion, S3 for raw storage,
  Spark for transformation, BigQuery for serving"
- Explain the data flow from source to consumer in one pass
- Do not go deep on any component yet
- The goal is a shared mental model between you and the interviewer

A good high-level design for a pipeline might look like:

```
Sources --> Kafka --> S3 (raw) --> Spark --> S3 (clean) --> Warehouse
                                                             |
                                                          Dashboards
```

### Minutes 10-30: Deep Dive (Interviewer-Guided)

The interviewer will pick 1-2 areas to explore. Follow their lead.

For each area:
- Explain the detailed design of that component
- Justify technology choices using the tradeoff framework (see
  `foundations/tradeoff_framework.md`): "I chose X over Y because..."
- Include numbers: throughput, storage, latency, cost
- Discuss failure modes: "If this component goes down, here is what happens
  and how we recover"
- Draw out the subcomponents if needed

This is where most of the evaluation happens. Depth matters more than breadth
in this phase.

### Minutes 30-40: Scaling, Evolution and Edge Cases

The interviewer will push your design to its limits.

Common questions to prepare for:
- "What happens at 10x current scale?"
- "How would you handle [specific failure scenario]?"
- "What if the latency requirement drops from hours to seconds?"
- "What would you change if the budget were cut by 50%?"

Show that you can think beyond the initial design. Identify which components
break first at scale, what you would change and what the cost implications
are.

### Minutes 40-45: Wrap Up

- Summarize your 2-3 key design decisions and their tradeoffs
- Mention what you would do differently with more time or information
- Ask if the interviewer wants to explore anything else

Do not introduce new components in the last 5 minutes. Consolidate and
clarify.

## Clarifying Questions to Always Ask

These questions are specific to data engineering interviews. Asking them
signals that you understand what matters in DE system design.

### Data Questions

- **Volume:** How many events per day? How many rows in the core tables?
  How many GB/TB total?
- **Velocity:** Is this batch (daily/hourly) or streaming (real-time)?
  What latency does the consumer need?
- **Variety:** Structured (relational), semi-structured (JSON, Avro) or
  unstructured (images, logs)?
- **Source:** Where does the data come from? APIs, databases, event
  streams, file drops?
- **Retention:** How long do we keep the data? Days, months, years, forever?

### Consumer Questions

- **Who reads this data?** Analysts running ad-hoc queries, dashboards
  refreshing every 5 minutes, ML models needing feature vectors, downstream
  systems consuming via API?
- **Latency requirement:** Must results be available in seconds, minutes or
  hours after the source event?
- **Query patterns:** Point lookups (get order by ID), scans (all orders
  last month), aggregations (total revenue by region)?
- **Concurrency:** How many simultaneous users or queries?

### Operational Questions

- **SLA:** What uptime and freshness guarantees are required?
- **Team size:** How many engineers will build and maintain this? (Affects
  build vs buy decisions significantly)
- **Budget:** What are the cost constraints? (Changes technology choices)
- **Existing infrastructure:** Already on AWS, GCP, Azure or on-prem?
  Multi-cloud or single provider?

## What NOT to Do

**Do not start drawing without asking questions.** The interviewer deliberately
leaves requirements ambiguous. Asking clarifying questions is part of the
evaluation.

**Do not go deep on one component before establishing the full picture.** If
you spend 20 minutes perfecting the ingestion layer, you will run out of time
before discussing storage, transformation or serving.

**Do not name technologies without explaining why.** "We will use Kafka" is
incomplete. "We will use Kafka because it handles our 50K events/sec
throughput requirement with ordering guarantees per partition and durable
storage for replay" is a design decision.

**Do not present a single option without alternatives.** "I would use Kafka,
though Kinesis would also work here. Kafka gives us more control over
partitioning and retention but requires more operational overhead. Given that
the team already runs Kafka, I would stick with it." This shows breadth.

**Do not ignore cost.** "This architecture costs approximately $X/month at
current scale" is a sentence that impresses interviewers. Use the numbers
from `foundations/capacity_estimation.md` to estimate this.

**Do not forget failure modes.** "If the streaming consumer falls behind,
Kafka retains messages for the configured retention period (default 7 days),
so we can catch up without data loss" shows operational maturity.

## Verbal Patterns That Work Well

These are phrases you can use almost verbatim. Practice them until they feel
natural.

### For Scoping

- "Let me make sure I understand the requirements..."
- "I will assume [X] unless you would like me to consider [Y] instead."
- "Before I start designing, can I ask about the expected volume and latency
  requirements?"
- "What is the primary consumer of this data? That will drive several design
  decisions."

### For Design Decisions

- "For [component], I see two main options: [A] and [B]."
- "[A] gives us [benefit] but costs us [tradeoff]."
- "Given our requirement for [specific constraint], I would go with [A]."
- "If that requirement changes, we would revisit this decision."

### For Capacity and Numbers

- "Let me do some quick math on the expected volume..."
- "At [X] events/sec and [Y] bytes/event, that is roughly [Z] GB/day."
- "The cost for that would be approximately $[N]/month on [service]."

### For Scaling Discussion

- "At 10x scale, the bottleneck moves from [X] to [Y]."
- "To handle that, we would [specific change], which adds [cost/complexity]."
- "The current design handles up to [threshold] before we need to
  [change strategy]."

### For Uncertainty

- "I am not 100% sure about the exact number, but my understanding is
  roughly [X]."
- "I would want to benchmark this before committing, but my estimate is [X]."
- "I am less familiar with [specific technology], but the general approach
  would be [Y]."

Honesty about uncertainty builds trust. Making up numbers destroys it.

## Connecting the Frameworks

This communication structure works best when combined with the other
foundations documents:

- Use the **tradeoff framework** (`foundations/tradeoff_framework.md`) during
  the deep-dive phase (minutes 10-30) to structure every design decision
- Use the **capacity estimation** guide ([`foundations/capacity_estimation.md`](capacity_estimation.md))
  during requirements gathering (minutes 0-5) and scaling discussion
  (minutes 30-40) to ground your design in concrete numbers
- Use the **pattern docs** ([`patterns/`](../patterns/) directory in this section) as the
  building blocks you combine during the high-level design phase

The interviewer is evaluating three things: can you think clearly about system
design, can you reason with numbers and can you communicate your thinking.
These three documents give you frameworks for all three.
