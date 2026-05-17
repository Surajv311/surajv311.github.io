---
layout: post 
title: Busy Spinning for High-Precision Market Replay in Go
category: technicalArticles
---

> From my experience working at [Punch](https://www.punch.trade/). Refactored my article a bit with help of GPT. 

I was building a system from scratch using a Go service with a NATS + JetStream stack to simulate and replay financial markets in a staging environment.

At a high level, live market ticks were persisted into JetStream streams, and the replay service consumed this historical data and re-published it onto NATS while preserving the original inter-tick timing. Replays could be triggered either through cron jobs or internal APIs, allowing downstream systems like charts and trading engines to behave similarly to live market conditions.

Financial markets such as the National Stock Exchange of India (NSE) and BSE Limited operate between 9:15 AM and 3:30 PM, during which financial instruments like stocks, futures, and options are actively traded.

The requirement was to enable replaying the market activity of a specific trading day outside market hours or during holidays. For example, if a team wanted to test a new trading or charting feature against real historical market conditions, the system could recreate the entire market session on demand in a controlled staging environment.

When replaying historical market data for testing or simulation, simply publishing messages as fast as possible is not enough. 

The inter-tick timing (the delay between consecutive market updates for stocks/F&O instruments) had to closely match the original market behavior to ensure charts, trading logic, and downstream systems behaved similarly to production.

I will discuss a few learnings related to building high-precision replay engine. 

**The Problem**: `time.Sleep(5 * time.Millisecond)` Is Not Precise. It guarantees a minimum sleep duration, not an exact wake-up time. The actual wake-up depends on: OS scheduler, timer granularity/resolution, CPU load, runtime scheduling, context switching, power-saving behavior, etc.

For high-frequency systems like market feeds, this can create timing errors. Eg:

```
Real market tick gap: 200µs
Replay gap using Sleep: 1ms
```

The replay timing becomes significantly slower than the original market behavior. A replay system must preserve these intervals. Eg: 

| Tick | Timestamp       |
| ---- | --------------- |
| T1   | 09:15:00.000000 |
| T2   | 09:15:00.000200 |
| T3   | 09:15:00.000450 |

Inter-tick gaps must be preserved:

```
T2 - T1 = 200µs
T3 - T2 = 250µs
```

**The Solution**: Busy Spinning. Instead of sleeping, the CPU can continuously check the clock until the desired time arrives. This technique is called busy spinning. Eg:

```go
target := time.Now().Add(delta)

for time.Now().Before(target) {
}
```

The loop repeatedly checks the current time until the target time is reached. Conceptually it works like this:

```
check time
check time
check time
check time
exit when target reached
```

**Why Busy Spinning Is Precise**: Modern systems implement `time.Now()` very efficiently. On Linux, Go uses: `clock_gettime(CLOCK_MONOTONIC)` via vDSO (Virtual Dynamic Shared Object). This means: No system call, No kernel context switch, Extremely fast execution. Typical cost: ~20–40 nanoseconds. 

So if we spin for 500 microseconds (theoretically):

```
500µs = 500,000ns
500,000 / 20 ≈ 25,000 iterations
```

The CPU checks the clock roughly 25,000 times, making the wait extremely accurate. Even with busy spinning, perfect determinism is not guaranteed because OS scheduling, goroutine preemption, and GC pauses can still introduce latency. However, it is significantly more precise than relying solely on `time.Sleep()` for sub-millisecond timing.

**Downside of Busy Spinning**: It consumes CPU.

**The Hybrid Strategy**: Sleep + Spin: A better approach in my use case was to combine both techniques. Strategy: Sleep most of the time; Busy-spin near the target time. 

This reduced CPU usage theoretically, although in practice I did not observe a significant difference in infrastructure metrics, likely because most inter-tick delays were already in the microsecond range.

Below is a simplified version of the approach used in the replay engine I worked on: 

```go
const defaultBusySpinThreshold = 2 * time.Millisecond
const sleepMargin = 1 * time.Millisecond

func WaitPrecise(delta time.Duration) {

    if delta <= 0 {
        return
    }

    target := time.Now().Add(delta)

    if delta > defaultBusySpinThreshold {

        sleepDuration := delta - sleepMargin

        if sleepDuration > 0 {
            time.Sleep(sleepDuration)
        }
    }

    for time.Now().Before(target) {
    }
}
```

How it works:

| Delay | Strategy     |
| ----- | ------------ |
| <2ms  | busy spin    |
| >2ms  | sleep + spin |

Example: Waiting for 10ms

```
sleepDuration = 10ms - 1ms = 9ms
So: 
|-------- sleep --------|-- spin --|
0                       9ms       10ms
```

CPU usage occurs only during the final 1ms. This avoids scheduler overshoot while preserving timing accuracy.

Also (as observed in sample code), instead of repeatedly sleeping for fixed intervals, we compute a target timestamp directly. This avoids cumulative drift, where small scheduling inaccuracies compound over thousands of ticks and eventually drift the replay by seconds.

Busy spinning is appropriate when: Precision below 1ms is required; Timing accuracy matters; Wait durations are short; CPU availability is acceptable. Else time.Sleep() is sufficient.

-----------------
