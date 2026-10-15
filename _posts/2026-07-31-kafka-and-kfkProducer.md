---
layout: post 
title: Kafka Producer Knobs 
category: technicalArticles
---

> From my experience working at [GreyOrange-Robotics](https://www.greyorange.com/). Refactored my article a bit with help of GPT. 

I was working on a service with a senior engineer that did some light processing and produced events to Kafka in the background. This component was a part of broader pipeline that had to be exactly-once semantics. Hence as part of work, I came across interesting producer configs, which I will discuss. 

Although before that, a quick brush up of Kafka. I am assuming below Kafka configs, based on which I will discuss few things, pretty similar to a setup I was working on: 

| Config | Value |
|---|---|
| **Kafka version** | 4.3.x (KRaft mode — no ZooKeeper) |
| **Brokers** | 3 |
| **Instance type** | Spot VMs, 1 broker per zone (3 zones) |
| **Replication factor** | 2 |
| **Retention** | 3 days |
| **Storage** | 220–250 GiB pd-balanced per broker (zonal) |
| **PodDisruptionBudget** | maxUnavailable: 1 |
| **Node pool** | Dedicated Spot pool, tainted, tolerations on Kafka pods |
| **Storage class** | pd-balanced (not local SSD) |

Three brokers, each pinned to a different GCP zone. Every partition has one leader and one follower — almost certainly in different zones.

- Kafka is a **durable, ordered, high-throughput log on a network**. You write messages into it (produce), and other systems read from it (consume) at their own pace. 
- **Topic**: A named stream of messages. Think of it like a table name or a named channel. Example: `warehouse.rack.size`.
- **Partition**: A topic is split into N ordered sub-logs called partitions. Each partition is an append-only file on disk. Messages within one partition are strictly ordered; across partitions, there is no ordering guarantee.

```
Topic: warehouse.rack.size  (4 partitions)

Partition 0:  [msg1] [msg5] [msg9]  [msg13] ──► (append-only)
Partition 1:  [msg2] [msg6] [msg10] ──►
Partition 2:  [msg3] [msg7] [msg11] ──►
Partition 3:  [msg4] [msg8] [msg12] ──►
```

- **Offset**: Every message in a partition has a monotonically increasing integer ID called an offset — like an array index. A consumer remembers "I've read up to offset 42 in partition 2" and picks up from there on restart.
- **Broker**: A single Kafka server process. It stores partitions on disk, accepts produce requests, and serves fetch requests to consumers. In a cluster, each broker owns a subset of partitions.
- **Producer**: Any process that writes messages to Kafka.
- **Consumer Group**: A set of processes that together read a topic. Kafka assigns each partition to exactly one consumer in the group at a time so the group reads every message exactly once as a whole under normal operation, with individual consumers each handling a subset of partitions.

```
Consumer Group "analytics" reading topic with 4 partitions

  Consumer A ◄── Partition 0, Partition 1
  Consumer B ◄── Partition 2, Partition 3

  Add a third consumer → Kafka rebalances:
  Consumer A ◄── Partition 0
  Consumer B ◄── Partition 1
  Consumer C ◄── Partition 2, Partition 3
```

---

- Multi-Broker Cluster Architecture: A single broker is a single point of failure and a throughput ceiling. In production you run a cluster. Three reasons: fault tolerance, throughput, and storage capacity.

- Every partition has one **leader** and zero-or-more **followers** (replicas). All produce and consume traffic goes to the leader. Followers pull from the leader to stay caught up called replication. 

```
Partition 0  (replication factor = 3)

  Broker 1 (LEADER) ──► Broker 2 (follower) ──► Broker 3 (follower)
       │                      │                       │
   writes go here       copies from leader      copies from leader
   reads go here

  If Broker 1 dies:
  Broker 2 or 3 is elected new leader → traffic shifts automatically
```

- Kafka spreads partition leaders evenly across brokers. With 12 partitions and 3 brokers, each broker leads roughly 4 partitions — distributing both CPU and network load.

```
3-broker cluster, 12 partitions:

  Broker 1: leads P0, P3, P6, P9    (also follows P1,P2,P4,P5,P7,P8,P10,P11)
  Broker 2: leads P1, P4, P7, P10
  Broker 3: leads P2, P5, P8, P11

In our 3-broker, RF=2 setup, each partition has 1 leader and 1 follower:
  Topic: orders  (4 partitions, replication factor: 2)
    Partition 0:  Leader → Broker 1 (zone-a)  |  Replica → Broker 2 (zone-b)
    Partition 1:  Leader → Broker 2 (zone-b)  |  Replica → Broker 3 (zone-c)
    Partition 2:  Leader → Broker 3 (zone-c)  |  Replica → Broker 1 (zone-a)
    Partition 3:  Leader → Broker 1 (zone-a)  |  Replica → Broker 3 (zone-c)
```

- Historically Kafka used **ZooKeeper** — a separate cluster — to store metadata: which broker is controller, which partitions have which leaders, ISR lists, etc. This meant running and maintaining a separate ZooKeeper ensemble alongside every Kafka cluster. Modern Kafka (3.x+) replaces this with **KRaft** — Kafka's own Raft-based consensus built directly in. Brokers elect a **controller** amongst themselves. No external dependency, simpler operations, and faster metadata operations. 

- A Produce request's journey through a cluster

```
1. Producer asks any broker: "who leads partition 2 of topic warehouse.events?"
2. Broker responds: "Broker 3 leads that partition"
3. Producer connects directly to Broker 3, sends the compressed batch
4. Broker 3 writes the batch to its local log
5. Broker 1, Broker 2 (followers) pull the batch and write to their local logs
6. Once ISR quorum acks, Broker 3 replies to producer: "OK, offset 10042"

Producer ──► Broker 3 (leader)
                  │
                  ├──► Broker 1 (follower, acks)
                  └──► Broker 2 (follower, acks)
                  │
                  └──► "OK, offset 10042" ──► Producer
```

**acks - Durability vs Throughput**
- When a producer sends a record, it can ask Kafka for different levels of confirmation before considering the write "done." This is the `acks` setting. 
  - **acks=0**: Fire and Forget. The producer sends the message and **does not wait for any acknowledgement** from the broker. As soon as the message hits the network socket buffer, the producer considers it sent. Kafka may or may not have written it to disk. If the broker crashes between receiving and persisting, the message is gone. The producer has no idea whether it was received. Returned offset is always `-1` (meaningless). Retries do nothing — the producer can't know what failed.
    - **When to use:** Metrics, logs, or telemetry where occasional loss is acceptable and maximum throughput is the goal. Never for financial, transactional, or auditable data.
    - **Throughput:** Maximum possible — no network roundtrip for acks.
  - **acks=1**: Leader Acknowledgement Only. The leader writes the record to its local log and immediately acknowledges the producer. It does **not** wait for followers to replicate. **The risk — "leader fails after ack, before follower replicates":**. On Spot VMs, evictions are sudden, the VM can vanish with little warning.
    - **When to use:** Medium-criticality streams where some data loss is tolerable but throughput matters.
    - **Throughput:** High — one network roundtrip, no follower coordination.
  - **acks=all (or acks=-1)**: Full ISR (in-sync replica) Acknowledgement. The leader waits until **all in-sync replicas** have written the record before acknowledging the producer. This is the strongest durability guarantee Kafka offers. The critical companion — min.insync.replicas: This sets the minimum number of in-sync replicas that must be available for Kafka to accept a write when using acks=all. For example:

    ```
    acks=all
    min.insync.replicas=2
    With replication.factor=3, a partition normally has three replicas:

    Broker A   Broker B   Broker C
       │          │          │
     leader     replica    replica

    If Broker C fails, the ISR can shrink to two replicas: ISR = {Broker A, Broker B}. Because ISR size (2) >= min.insync.replicas (2), Kafka can continue accepting writes with acks=all.

    If another replica falls out of the ISR: ISR = {Broker A}. Then ISR size (1) < min.insync.replicas (2), so Kafka rejects the write rather than acknowledging a record that has fewer than the required number of in-sync replicas.

    This is why a common production configuration is as described earlier: replication.factor=3, min.insync.replicas=2, acks=all. It allows the cluster to continue accepting writes after losing one replica while still requiring two in-sync replicas for acknowledged writes.
    
    Important for an RF=2 cluster: If your topic has replication.factor=2 and min.insync.replicas=2, losing either replica leaves only one replica in the ISR, so acks=all writes will fail until the ISR is restored. RF=2 therefore provides less write availability during a broker failure than RF=3 with min.insync.replicas=2.
    ```
    
    - **When to use:** Any data where loss is unacceptable. Required for idempotent and exactly-once producers.
    - **Throughput:** Lower than acks=1 — the roundtrip includes follower replication latency. In a same-region multi-zone cluster, this is typically 5–20ms added latency.

**batch.size and linger.ms — Throughput Tuning**
- The producer accumulates records into batches before sending. Two configs control when a batch is flushed:
  - **`batch.size`** — maximum bytes in a single produce batch. Once a batch hits this size, it is sent immediately.
  - **`linger.ms`** — how long the producer waits to fill a batch before sending even if it isn't full yet. Default is `5` in Kafka 4.x. In older versions it used to be 0ms (send immediately).
  - Setting `linger.ms` to 5–20ms dramatically improves throughput on high-volume topics by allowing more records to accumulate per batch, at the cost of tiny and usually imperceptible latency increases. 

```
linger.ms=0:
  Record arrives → batch sent immediately (low latency, low throughput)

linger.ms=10:
  Record arrives → wait up to 10ms → more records accumulate → larger batch sent
  (slightly higher latency, dramatically better throughput)
```

**max.in.flight.requests.per.connection — Parallelism vs Ordering**
- How many produce requests can be in-flight simultaneously to one broker. More in-flight requests = more parallelism = higher throughput. But there is a catch:
- Without idempotence: if you send batches A and B, A fails and retries after B succeeds, the partition log ends up with B before A — **ordering is violated**.
- With the **idempotent producer**, this is capped at **5** — Kafka's enforced maximum that still maintains ordering via sequence numbers. You get parallelism without reordering risk.

```properties
# With idempotent producer (required):
max.in.flight.requests.per.connection=5   # max allowed; kafka enforces ordering via seq numbers

# Without idempotence (higher throughput, ordering risk):
max.in.flight.requests.per.connection=10+  # reordering possible on retry
```

**ProduceRequestTimeout — Single RPC Timeout**
- How long the producer waits for a response to a single produce RPC. If the broker does not respond in this window, the request fails and is retried. Think of it as: *"how patient am I with one individual network call?"*
  - Too low → spurious timeouts under transient load spikes trigger unnecessary retries.
  - Too high → a stuck broker ties up the producer for a long time before retrying.

```properties
request.timeout.ms=5000   # 5 seconds per RPC attempt
```

**RecordDeliveryTimeout — Total Retry Budget per Record**
- Kafka clients retry failed batches automatically. `delivery.timeout.ms` sets the upper bound on how long the producer will attempt to deliver a record, including retries. It is not a fixed number of retry attempts. The relationship between the two:
  - `request.timeout.ms` = timeout for **one attempt**
  - `delivery.timeout.ms` = total budget across **all attempts**
  - `delivery.timeout.ms` must be ≥ (`request.timeout.ms` + `linger.ms`)

```
t=0:00  Record enqueued, Kafka unreachable
t=0:05  Retry 1 → still unreachable (RPC timeout: 5s)
t=0:15  Retry 2 → still unreachable
t=0:30  Retry 3 → ...
...
t=2:00  delivery.timeout.ms expires → ErrRecordTimeout
        → record is dropped, callback fires with error
```

```properties
delivery.timeout.ms=120000   # 2 minutes total retry window
```

**MaxBufferedRecords — In-Memory Cap**
- The producer keeps an internal in-memory buffer of records waiting to be batched and sent. Depending on your client implementation you can buffer based on size or number of records. 
- When the buffer is full (e.g., Kafka is unreachable and records pile up), new produce attempts are rejected immediately — no blocking, no OOM.
- Without a cap, a slow or dead broker causes the producer to accumulate records in memory until the process OOMs. The cap trades *some* data loss for process stability — an acceptable trade-off for most systems. Eg: 

| Bound | Value | Reason |
|---|---|---|
| Too low | < 5,000 | Buffer drains too fast under normal bursts |
| Reasonable default | 50,000 | Safe starting point for moderate write rates |
| Upper guard | 500,000 | Beyond this, memory pressure becomes real |

```
HTTP request → produce() → [internal buffer, max N records]
                                    │
                                    └──► batcher → broker → ack
If buffer fills (Kafka unreachable):
  produce() → ErrMaxBuffered → caller handles the drop
```

**ProducerBatchCompression — Compress Before Sending**
- The producer compresses entire **batches** (not individual messages) before sending to the broker. zstd achieves better ratios than gzip/snappy at similar CPU cost. Compressing at batch level amortises the CPU cost across many records per batch.
- **Note**: also set `compression.type=producer` on the kafka broker topic. This tells the broker: *"store batches exactly as I sent them, do not recompress."* Without this, the broker may decompress your zstd batch and re-compress with the cluster default codec — wasting CPU on both ends and potentially changing the wire format for downstream consumers.

| Codec | Ratio | CPU cost | When to use |
|---|---|---|---|
| `gzip` | Highest | Highest | Legacy; rarely the right choice today |
| `snappy` | Lower | Very low | CPU-bottlenecked producers |
| `lz4` | Good | Low | Strong default on constrained CPU budgets |
| `zstd` | Often beats gzip | Lower than gzip | Good general-purpose default |

```properties
compression.type=zstd   # on the producer
```

**Idempotent Producer: Eliminating Duplicates on Retry**
- Every messaging system makes one of three promises about delivery.

| Guarantee | What It Means | Risk |
|---|---|---|
| **At-most-once** | A message might be lost. Never delivered twice. | Data loss |
| **At-least-once** | Eventually delivered. Might be delivered more than once. | Duplicates |
| **Exactly-once** | Delivered exactly once. No loss, no duplicates. | Requires deliberate config |

- Even with `acks=all`, there is a subtle problem: **producer retries create duplicates.**

```
Producer                    Broker
   │                            │
   ├──── Batch (seq=0) ────────►│  broker writes to log, prepares ack
   │                            │
   │         [network blip]     │
   │◄──── (ack never arrives)   │
   │                            │
   │  "I didn't get an ack,     │
   │   I'll retry"              │
   ├──── Batch (seq=0) ────────►│  ← broker writes it AGAIN (duplicate!)
   │◄──── "OK" ─────────────────│
```

- The producer cannot distinguish "ack was lost" from "write failed." So it retries. The broker, without idempotence, has no memory of the first write. You get a duplicate record.
- Idempotent producer tries to solve this, enabled via: `enable.idempotence=true` (modern clients enable this by default when `acks=all`). It works by: 
  - The broker assigns the producer a **Producer ID (PID)** — a unique integer for this producer instance's lifetime.
  - Each partition gets its own monotonically increasing **sequence number**.
  - Every batch is stamped with `(PID, partition, sequence_number)`.
  - If the broker receives a batch with a sequence number it has already written, it accepts the request (returns success) but **silently discards the duplicate**.

```
Producer (PID = 42)              Broker
     │                               │
     ├── Batch (seq=0) ─────────────►│  written; seq=0 recorded for PID 42
     │          [ack lost]            │
     ├── Batch (seq=0) ─────────────►│  "already have seq=0 for PID 42 — discard"
     │◄────── "OK" ──────────────────│  producer thinks it succeeded (it did, the first time)
     │                               │
     ├── Batch (seq=1) ─────────────►│  written; seq=1 recorded
     │◄────── "OK" ──────────────────│
```

- Caveat: PID resets on producer restart: The PID is assigned fresh on each producer startup. If the process crashes and a new instance starts, it gets a new PID. The broker will not recognise retry attempts from the new instance as duplicates of the old one. A record that was in-flight at crash time could be written twice — once by the old instance (before crash) and once by the new instance (on startup retry). For most telemetry and event-streaming workloads, a single duplicate point on a process restart is acceptable — it is a known, bounded limitation of the idempotent producer without full transactions.
- Idempotent producer gives you exactly-once *from producer to broker* within a single session. It does **not** give you:
  - Exactly-once across multiple topics simultaneously
  - Exactly-once from broker to consumer (the consumer commits its own offsets separately)
  - End-to-end exactly-once across the full pipeline (producer → Kafka → consumer → database)
  - Exactly-once across producer restarts (PID resets)

For those, you need **Kafka Transactions**. But I read online, that if related configs are not tuned properly then Kafka transactions hurt throughput. 

```
Eg: Transactions: Atomic Multi-Partition Writes
Producer:
  beginTransaction()
    write(topic=A, partition=0, message=M1)
    write(topic=B, partition=2, message=M2)
  commitTransaction()   ← both M1 and M2 become visible atomically
  # or
  abortTransaction()    ← neither M1 nor M2 becomes visible
```

- A **transactional producer** is assigned a stable `transactional.id` that persists across restarts. When the producer restarts, it uses the same transactional.id to recover transactional state and fence the previous instance, providing transactional guarantees across restarts.
  - **Producer config for full exactly-once semantics:**

    ```properties
    enable.idempotence=true
    transactional.id=my-unique-producer-id    # stable across restarts
    acks=all
    ```

  - **Consumer config — only read committed messages:**: Without `read_committed`, consumers see messages from uncommitted (in-flight) transactions — which may later be aborted, causing **phantom reads**: the consumer processes a message that was never actually committed.

    ```properties
    isolation.level=read_committed
    ```

**Other info**: 
- Partition Key — Routing and Ordering: The record key controls which partition a record lands in. Records with the same key always go to the same partition (for a fixed partition count). Records with a `null` key are distributed by the client.
  - **Keyed records:** gives ordering guarantees — all records for the same key arrive at the same partition in order. The risk: if one key generates disproportionately high traffic, one partition gets disproportionate load — the hot partition problem. A more granular key (e.g., `user_id + metric_type`) distributes load across partitions while still giving ordering within a category.
  - **Null-keyed records:** since Kafka 2.4, the default partitioner for null-keyed records is the **sticky partitioner**, not round-robin. It writes to one partition until a batch fills or `linger.ms` expires, then rotates. This meaningfully improves batch fill rates on high-volume keyless topics over round-robin. If you need key identity for consumers (for routing or filtering) but don't want it to affect partitioning, put it in a **record header** instead of the key.
- A producer does not fail immediately when a broker becomes unreachable. Retries and buffering absorb short outages transparently.
- Two decisions made at topic creation that you mostly can't undo:
  - **Partition count** — more partitions = more consumer parallelism, but also more replication overhead at the cluster level (100 partitions × 3 replicas = 300 replica slots to manage). Partition count should be sized from expected producer throughput, consumer parallelism, recovery requirements, and broker capacity. Kafka can **add** partitions to an existing topic. It **cannot remove them**. If you auto-create topics programmatically, guard against a config service returning a nonsense value (like 50,000 partitions) with a hard cap, and make sure your reconciliation logic only ever increases partition count, never decreases.
  - **Replication factor** — typically 3 in production. With `min.insync.replicas=2` and `acks=all`, you can lose one broker and keep writing without pause.  
- Running Kafka on Spot VMs is economical but introduces real eviction risk.
- When your process shuts down, records may still be sitting in the buffer or a linger window, unsent. The correct pattern:
  - Stop accepting new records.
  - Call `flush()` with a reasonable timeout — give in-flight records a chance to drain.
  - Call `close()`. Ensure the client library doesn't skip pending callbacks/flush(), as the object is being torn down.


------------------------------------



 
