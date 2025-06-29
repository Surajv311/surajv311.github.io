---
layout: post
title: Kafka Consumers
category: technicalArticles
---

> From my experience working at [Simpl](https://simpl.com/).

A few days ago, I was working on a project when I got distracted by an error originating from one of the Kafka consumers our team owns.
The consumers read events from Kafka, add some metadata, and dump it in S3. It's a python based microservice running on AWS ECS.

There are conditions attached before the data is flushed to S3 like: Either the memory buffer size is breached (eg: 10mb), or the time to hold data in buffer is expired (eg: 10mins).

Now, the error was: `KafkaError{code=_MAX_POLL_EXCEEDED,val=-147,str="Application maximum poll interval (300000ms) exceeded by 249ms"}`.
Working on this issue gave me a reason to deep dive into the Kafka consumer code and understand how it works.

```
# Pseudocode: 

from confluent_kafka import Consumer, KafkaError

class KafkaConsumer:
    def __init__(self, config: dict = {}, topics: str = None, auto_commit: bool = True):
        self.auto_commit = auto_commit
        self.conf = {
            'bootstrap.servers': 'localhost:9092',
            'group.id': 'groupid-1',
            'session.timeout.ms': 60000,
            'security.protocol': 'PLAINTEXT',
            'default.topic.config': {'auto.offset.reset': 'smallest'},
            'enable.auto.commit': self.auto_commit,
        }
        self.conf.update(config)
        if topics is None or topics == '':
            raise Exception('You must provide atleast one topic. eg, "topic1,topic2"')
        self.topics = [t.strip() for t in topics.split(',')]
        self._consumer = Consumer(**self.conf)

    def _subscribe(self):
        self._consumer.subscribe(self.topics)
        log.info(f"Subscribed to topic {self.topics}")
        # Reset consumer to a specific time or offset if needed to reprocess messages.
        reset_hours_back = None
        if reset_hours_back:
            self._reset_to_hours_back(reset_hours_back)

    def stream(self, poll_timeout=1.0):
        self._subscribe()
        while True:
            try:
                msg = self._consumer.poll(timeout=poll_timeout)
                if msg is None:
                    log.debug("Polling from kafka..")
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    else:
                        yield (None, msg.error())
                data = msg.value().decode('utf-8')
                yield (data, None)
            except Exception as e:
                yield (None, e)

    def commit_offsets(self, asynchronous=False):
        return self._consumer.commit(asynchronous=asynchronous)
    
class KafkaToS3ConsumerService:
    def __init__(self):
        self.buffer_event_count = 10000
        self.blockSize = int(config.BLOCK_SIZE)
        self.bufferExpireLimit = int(config.BUFFER_EXPIRE_LIMIT)
        self.topics = os.environ['S3_CONSUMER_KAFKA_TOPICS']
        self.conf = config.kafka_config
        self.tempFile = {}
        self.tempFileList = {}
        self.currentBufferSize = {}
        self.meta_dict = {}
        self.offsetStatistics = {}
        self.processingStartTime = time.monotonic()
        self.accumulation_start_time = None
        self.count = 0

    def consume(self):
        self.conf['on_commit'] = self.offset_commit_callback
        kafka = KafkaConsumer(config=self.conf, topics=self.topics, auto_commit=False)
        for event, error in kafka.stream():
            if error:
                notify_ims_systems(str(error)) # notifying incident management systems like: pagerduty/sentry etc. 
            if event:
                try:
                    self.buffer_data(event)
                    buffer_size_expired_flag = self.__check_buffer_size_expiration()
                    buffer_time_expired_flag = self.__check_buffer_time_expiration()
                    if buffer_time_expired_flag or buffer_size_expired_flag:
                        if self.__has_data():
                            self.close_file_and_reset_buffer()
                            kafka.commit_offsets(asynchronous=False)
                            self.accumulation_start_time = None
                            log.debug("Uploaded local temp files to S3. Buffer is reset")
                except Exception as e:
                    tb = traceback.format_exc()
                    log.error(f"Errors were found in following batch traceback: {tb}")
                    notify_ims_systems(f'Error while processing event. Error: {str(e)}, traceback: {tb}, event: {event}')
```

There are three fundamental concepts related to the kafka consumers:

* **Polling**: The mechanism for fetching messages from brokers
* **Heartbeating**: The mechanism for maintaining group membership
* **Offset Management**: The mechanism for tracking processing progress

But before I dive into them, a quick detour on Kafka architecture: 
```
1) 
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                        Complete Kafka Architecture                                       │
├───────────────────────────────────────────────────────────────────────────────────────────────────────── ┤
│                                                                                                          │
│  Producers                                    Kafka Cluster                               Consumers      │
│                                                                                                          │
│ ┌─────────────┐                          ┌─────────────────────────┐                 ┌─────────────┐     │
│ │   Web App   │──┐                       │                          │              ┌─│  Analytics  │     │
│ │ (UserEvents)│  │    Produce            │  ┌─────────────────────┐ │   Consume    │ │   Service   │     │
│ └─────────────┘  │   Requests            │  │      Broker 1       │ │  Requests    │ └─────────────┘     │
│                  │                       │  │ ┌─────────────────┐ │ │              │                     │
│ ┌─────────────┐  │                       │  │ │ user-events     │ │ │              │ ┌─────────────┐     │
│ │Mobile App   │──┼──────────────────────►│  │ │ Partition 0 (L) │ │ │◄─────────────┼─│   Billing   │     │
│ │(OrderEvents)│  │                       │  │ └─────────────────┘ │ │              │ │   Service   │     │
│ └─────────────┘  │                       │  │ ┌─────────────────┐ │ │              │ └─────────────┘     │
│                  │                       │  │ │ order-events    │ │ │              │                     │
│ ┌─────────────┐  │                       │  │ │ Partition 0 (L) │ │ │              │ ┌─────────────┐     │
│ │   API       │──┼──────────────────────►│  │ └─────────────────┘ │ │◄─────────────┼─│Notification │     │
│ │ Gateway     │  │                       │  └─────────────────────┘ │              │ │   Service   │     │
│ └─────────────┘  │                       │                          │              │ └─────────────┘     │
│                  │                       │  ┌─────────────────────┐ │              │                     │
│ ┌─────────────┐  │                       │  │      Broker 2       │ │              │ ┌─────────────┐     │
│ │   IoT       │──┼──────────────────────►│  │ ┌─────────────────┐ │ │◄─────────────┼─│   Audit     │     │
│ │  Sensors    │  │                       │  │ │ user-events     │ │ │              │ │   Service   │     │
│ └─────────────┘  │                       │  │ │ Partition 1 (L) │ │ │              │ └─────────────┘     │
│                  │                       │  │ └─────────────────┘ │ │              │                     │
│ ┌─────────────┐  │                       │  │ ┌─────────────────┐ │ │              │ ┌─────────────┐     │
│ │  Batch      │──┘                       │  │ │ order-events    │ │ │◄─────────────┼─│   Stream    │     │
│ │ Processor   │                          │  │ │ Partition 1 (L) │ │ │              │ │ Processor   │     │
│ └─────────────┘                          │  │ └─────────────────┘ │ │              │ └─────────────┘     │
│                                          │  └─────────────────────┘ │              │                     │
│  Configuration:                          │                          │              │ Consumer Groups:    │
│  • acks=all                              │  ┌─────────────────────┐ │              │ • analytics-group   │
│  • retries=3                             │  │      Broker 3       │ │              │ • billing-group     │
│  • batch.size=16384                      │  │ ┌─────────────────┐ │ │              │ • notification-grp  │
│  • compression=gzip                      │  │ │ user-events     │ │ │              │ • audit-group       │
│                                          │  │ │ Partition 2 (L) │ │ │              │ • stream-processor  │
│                                          │  │ └─────────────────┘ │ │              │                     │
│                                          │  │ ┌─────────────────┐ │ │              │ Configuration:      │
│                                          │  │ │ order-events    │ │ │              │ • auto.offset.reset │
│                                          │  │ │ Partition 2 (L) │ │ │              │ • enable.auto.commit│
│                                          │  │ └─────────────────┘ │ │              │ • max.poll.records  │
│                                          │  └─────────────────────┘ │              │ • fetch.min.bytes   │
│                                          └─────────────────────────┘               │                     │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────┘

2) Consumer Group Rebalancing

Before Rebalancing (3 consumers, 6 partitions):
┌─────────────────────────────────────────────────────────────────┐
│                Consumer Group: "data-processors"                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ Consumer A        Consumer B        Consumer C                  │
│ ┌─────────────┐   ┌─────────────┐   ┌─────────────┐             │
│ │ Partition 0 │   │ Partition 2 │   │ Partition 4 │             │
│ │ Partition 1 │   │ Partition 3 │   │ Partition 5 │             │
│ └─────────────┘   └─────────────┘   └─────────────┘             │
└─────────────────────────────────────────────────────────────────┘

Consumer B Crashes:
┌─────────────────────────────────────────────────────────────────┐
│                     Rebalancing Triggered                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ Consumer A        Consumer B        Consumer C                  │
│ ┌─────────────┐   ┌─────────────┐   ┌─────────────┐             │
│ │   Active    │   │  CRASHED    │   │   Active    │             │
│ │             │   │     ❌      │   │             │             │
│ └─────────────┘   └─────────────┘   └─────────────┘             │
│        │                                   │                    │
│        └─────────────┬─────────────────────┘                    │
│                      │                                          │
│              Group Coordinator                                  │
│                 Redistributes                                   │
│                  Partitions                                     │
└─────────────────────────────────────────────────────────────────┘

After Rebalancing (2 consumers, 6 partitions):
┌─────────────────────────────────────────────────────────────────┐
│                Consumer Group: "data-processors"                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ Consumer A                    Consumer C                        │
│ ┌─────────────────────────┐   ┌─────────────────────────┐       │
│ │ Partition 0             │   │ Partition 3             │       │
│ │ Partition 1             │   │ Partition 4             │       │
│ │ Partition 2             │   │ Partition 5             │       │
│ └─────────────────────────┘   └─────────────────────────┘       │
└─────────────────────────────────────────────────────────────────┘

3) Message Partitioning Strategies:

a. Key-based Partitioning (Default):
┌─────────────────────────────────────────────────────────────────┐
│ Producer Messages:                                              │
│                                                                 │
│ Message 1: key="user123" → hash(user123) % 3 = 0 → Partition 0  │
│ Message 2: key="user456" → hash(user456) % 3 = 1 → Partition 1  │
│ Message 3: key="user789" → hash(user789) % 3 = 2 → Partition 2  │
│ Message 4: key="user123" → hash(user123) % 3 = 0 → Partition 0  │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Topic: user-events                           │
├─────────────────────────────────────────────────────────────────┤
│ Partition 0        Partition 1        Partition 2               │
│ ┌─────────────┐    ┌─────────────┐    ┌─────────────┐           │
│ │ user123:msg1│    │ user456:msg2│    │ user789:msg3│           │
│ │ user123:msg4│    │             │    │             │           │
│ └─────────────┘    └─────────────┘    └─────────────┘           │
└─────────────────────────────────────────────────────────────────┘

b. Others like Round robin based, etc... 

4) Kafka ecosystem: 
Core Components
    Kafka Broker: The server that stores and serves messages. Multiple brokers form a Kafka cluster.
    Producer: Client application that publishes/sends messages to Kafka topics.
    Consumer: Client application that reads/subscribes to messages from Kafka topics.
    Topics: Named streams or categories where messages are published and organized.
    Partitions: Subdivisions of topics that enable parallel processing and scalability.
    Offsets: Sequential IDs assigned to messages within partitions for tracking read position.
Supporting Components
    Zookeeper: Coordination service for managing cluster metadata, leader election, and configuration.
    Consumer Groups: Groups of consumers that coordinate to process messages from topics in parallel.
    Replication: Copies of partition data across multiple brokers for fault tolerance.
    Leader/Follower: Leader handles reads/writes for a partition; followers replicate the data.
```

Now, Kafka consumers operate within consumer groups:

```
Topic: user-events (3 partitions)
┌─────────────┬─────────────┬─────────────┐
│ Partition 0 │ Partition 1 │ Partition 2 │
└─────────────┴─────────────┴─────────────┘
       │             │             │
       ▼             ▼             ▼
┌─────────────┬─────────────┬─────────────┐
│ Consumer A  │ Consumer B  │ Consumer C  │
│ (Group: X)  │ (Group: X)  │ (Group: X)  │
└─────────────┴─────────────┴─────────────┘
```

Each consumer in a group is assigned specific partitions, and the group coordinator (a Kafka broker) manages these assignments.

The `poll()` method is the heart of Kafka consumer operation, but it does much more than just fetch messages. 
I tried to go through the source code but realized it's a maze, maybe I will spend more time on this later - https://github.com/confluentinc/librdkafka/blob/master/src/rdkafka.c#L3388.

Here's what a typical polling sequence looks like:

```
Time    Action                           Duration    Notes
─────────────────────────────────────────────────────────────
0:00:00 poll() called                   0ms         Start
0:00:00 Check internal buffer           <1ms        500 msgs available
0:00:00 Return 1 message                <1ms        From buffer
0:00:00 Process message                 1ms         Your application
0:00:01 poll() called again             0ms         Start next cycle
0:00:01 Check internal buffer           <1ms        499 msgs available
0:00:01 Return 1 message                <1ms        From buffer
...     (continues until buffer empty)
0:02:30 poll() called                   0ms         Buffer now empty
0:02:30 Send fetch request to broker    50ms        Network call
0:02:30 Receive 500 new messages        <1ms        Broker response
0:02:30 Return 1 message                <1ms        First from new batch
```

Note:
- Polling only happens when your application code explicitly calls `poll()` & not automatically every X seconds.
- poll_timeout=1.0 is not the polling interval of 1s; it's the maximum time to wait for messages if none are immediately available.
- Heartbeats & polling are different concepts. We will learn more on it, but heartbeats run in the background by the consumer client to maintain group membership, while polling is your main thread's way of fetching messages. If poll() is not called within max.poll.interval.ms, the consumer is considered stalled or dead, even if heartbeats are working. Ref: https://stackoverflow.com/a/40200328 

Relation & differences between Heartbeats/Poll/Session intervals: 

We can understand with an example directly. But info around configs involved in tweaking the related intervals: 

```python
consumer_config = {
    # How often to send "I'm alive" signals
    'heartbeat.interval.ms': 3000,        # 3 seconds
    
    # How long without heartbeat before considered dead
    'session.timeout.ms': 30000,          # 30 seconds
    
    # How long between poll() calls before considered stuck
    'max.poll.interval.ms': 300000,       # 5 minutes (default)
}
```

```
Timeline: Consumer Processing a Large Batch
│
├── 0s ──────── poll() called, gets batch
│   │
│   ├── 3s ──── Heartbeat sent (background)
│   │
│   ├── 6s ──── Heartbeat sent (background)
│   │
│   ├── 9s ──── Heartbeat sent (background)
│   │
│   ├── 12s ─── Heartbeat sent (background)
│   │
│   ├── 15s ─── Processing continues...
│   │
│   ├── 30s ─── Still within session.timeout.ms ✓
│   │
│   ├── 60s ─── Still processing, heartbeats continuing
│   │
│   ├── 300s ── MAX_POLL_INTERVAL EXCEEDED! ❌
│   │
│   └── ERROR: Consumer removed from group
```

```python
fetch_config = {
    # Maximum records in one poll() call
    'max.poll.records': 500,
    
    # Minimum bytes to fetch (efficiency)
    'fetch.min.bytes': 1,
    
    # Maximum bytes per fetch request
    'fetch.max.bytes': 52428800,  # 50MB
    
    # Max wait time for min bytes
    'fetch.max.wait.ms': 500,
}
```

A message journey from Kafka to broker would look like below:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Kafka Broker  │    │ Consumer Client │    │ Your Application│
│                 │    │                 │    │                 │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │   Topic     │ │    │ │   Internal  │ │    │ │    Temp     │ │
│ │ Partition 0 │ │    │ │   Buffer    │ │    │ │   Files     │ │
│ │ [msg1]      │ │    │ │   (500 msg) │ │    │ │  (10k msg)  │ │
│ │ [msg2]      │ │    │ │             │ │    │ │             │ │
│ │ [msg3]      │ │    │ │             │ │    │ │             │ │
│ │  ...        │ │    │ │             │ │    │ │             │ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │ 1. fetch_request      │                       │
         │◄──────────────────────│                       │
         │                       │                       │
         │ 2. 500 messages       │                       │
         │──────────────────────►│                       │
         │                       │ 3. poll() returns     │
         │                       │     1 message         │
         │                       │─────────────────────► │
         │                       │                       │
         │                       │ 4. process & buffer   │
         │                       │◄───────────────────── │
         │                       │                       │
         │                       │ 5. repeat 499 times   │
         │                       │◄────────────────────► │
```

I think by now we have some picture of what could have led to the MAX_POLL_EXCEEDED error, but let's continue. 

Kafka consumer application actually has multiple types of buffers:

* **Kafka Broker Storage** (Not a buffer, but the source)
  * Location: Kafka broker disk
  * Purpose: Persistent message storage
  * Size: Configured per topic/partition

* **Consumer Client Internal Buffer**
  * Location: Your application's heap memory
  * Purpose: Pre-fetch messages for efficiency
  * Size: Controlled by `max.poll.records` and fetch settings
  * Management: Automatically managed by consumer client

* **Your Application Buffers**
  * Location: Your application memory/temp files
  * Purpose: Batch processing, business logic
  * Size: Controlled by your application logic
  * Management: Your responsibility

```python
# Example of the three buffer types in code
class KafkaToS3ConsumerService:
    def consume(self):
        kafka = KafkaConsumer(...)  # Creates consumer with internal buffer
        for event, error in kafka.stream():  # Gets 1 msg from internal buffer
            # This is the application buffer
            self.buffer_data(event)  # Write to temp files
            if self.should_flush_buffer():
                self.upload_to_s3()  # Process your application buffer
```

The memory usage over time would look like (considering our consumer code): 

```
Kafka Internal Buffer (500 messages):
████████████████████████████████████████  (constant ~50MB)

Your Application Buffer (accumulating):
▁▂▃▄▅▆▇█ (grows) → flush to S3 → ▁ (reset) → ▁▂▃▄▅▆▇█ → flush...
```

Apart from poll interval which we discussed earlier, there is also: `poll timeout`.

**Poll Timeout (`timeout` parameter in `poll(timeout)`)**:
```python
msg = consumer.poll(timeout=1000)  # Wait UP TO 1 second for messages
```

* Purpose: How long to wait when no messages are available
* Behavior: Returns immediately if messages are available
* Impact: Only affects CPU usage and responsiveness when queue is empty

**Poll Interval (`max.poll.interval.ms` configuration)**:
```python
config = {
    'max.poll.interval.ms': 300000  # Must call poll() within 5 minutes
}
```

* Purpose: Maximum time allowed between consecutive `poll()` calls
* Behavior: Enforced by Kafka broker, not client
* Impact: Consumer removed from group if exceeded

For example: 

**Normal Operation (Fast Processing)**:
```
0:00:00 poll() → get message → process (100ms) → poll() → get message...
        ↑────── 10ms between polls ──────↑
        Interval: 100 ms (less than default 5 minutes)
        Timeout: 0ms (as messages readily available)
To imagine better: 
Time Window: 0-200ms
┌─────────────────────────────────────────────────────────────┐
│ poll()      │ process │ poll()      │ process │ poll()      │
│ ┌─────────┐ │ ┌─────┐ │ ┌─────────┐ │ ┌─────┐ │ ┌─────────┐ │
│ │ 0ms     │ │ │100ms│ │ │ 0ms     │ │ │100ms│ │ │ 0ms     │ │
│ │(instant)│ │ │     │ │ │(instant)│ │ │     │ │ │(instant)│ │
│ └─────────┘ │ └─────┘ │ └─────────┘ │ └─────┘ │ └─────────┘ │
└─────────────────────────────────────────────────────────────┘
      ↑─────────────↑         ↑─────────────↑
    Poll Timeout: 0ms    Poll Interval: 100ms
    (messages ready)     (very fast)
```

**Slow Processing Operation**:
```
0:00:00 poll() → get message → process (6 minutes) → poll()
        ↑────────── 6 minutes between polls ──────────↑
        Interval: 6 minutes (exceeds default 5 minutes, processing took time)
        Timeout: 0ms (as messages readily available)
Result: MAX_POLL_EXCEEDED error because 6min > 5min limit
To imagine better: 
Time Window: 0-7 minutes
┌─────────────────────────────────────────────────────────────┐
│ poll() │         Long Processing (S3 Upload)        │ poll()│
│ ┌────┐ │ ┌─────────────────────────────────────────┐ │ ┌──┐ │
│ │0ms │ │ │                6 minutes                │ │ │❌│ │
│ │msg │ │ │          (no poll() calls)              │ │ │  │ │
│ └────┘ │ └─────────────────────────────────────────┘ │ └──┘ │
└─────────────────────────────────────────────────────────────┘
    ↑─────────────────────────────────────────────────────↑
  Poll Timeout: 0ms              Poll Interval: 6 minutes
  (message ready)                (EXCEEDS 5min limit!)
                                 MAX_POLL_EXCEEDED ERROR
```

**Empty Queue Scenario**:
```
0:00:00 poll(timeout=1000) → wait 1sec → return None → poll(timeout=1000)...
        ↑────────── 1 second between polls ──────────↑
        Interval: 1000ms (as no messages available, window closing for new messages based on timeout defined)
        Timeout: 1000ms (as specified in poll)
To imagine better: 
Time Window: 0-3 seconds
┌─────────────────────────────────────────────────────────────┐
│ poll()                    │ poll()                    │     │
│ ┌───────────────────────┐ │ ┌───────────────────────┐ │     │
│ │ 1000ms                │ │ │ 1000ms                │ │     │
│ │ (waiting for messages)│ │ │ (waiting for messages)│ │     │
│ │ returns None          │ │ │ returns None          │ │     │
│ └───────────────────────┘ │ └───────────────────────┘ │     │
└─────────────────────────────────────────────────────────────┘
        ↑─────────────────────────↑─────────────────────────↑
      Poll Timeout: 1000ms   Poll Interval: 1000ms
      (queue empty)          (controlled by timeout)
```

Next, let's talk about the offset management and commits, which is crucial for understanding how Kafka tracks message processing progress and ensures reliability in message consumption.

**Polling** (fetching messages):
```python
records = consumer.poll(timeout=1000)  # Gets messages to process
```
* **Purpose**: Retrieve messages from Kafka
* **Effect**: Updates internal position tracking
* **Does NOT**: Tell Kafka you've processed the messages

**Committing** (confirming processing):
```python
consumer.commit()  # Tells Kafka: "I've processed messages up to offset X"
```
* **Purpose**: Persist your processing progress
* **Effect**: Updates the `__consumer_offsets` topic
* **Determines**: Where to resume after restart/rebalance

Commit behaviour: 

**Auto-Commit Behavior**:
```python
config = {
    'enable.auto.commit': True,
    'auto.commit.interval.ms': 5000  # Commit every 5 seconds
}

# Timeline:
# 0s: poll() and process messages
# 3s: poll() and process messages  
# 5s: auto-commit happens (commits all polled messages)
# 6s: poll() and process messages
# 10s: auto-commit happens again
```

**Manual Commit Behavior** (Your Code):
```python
config = {
    'enable.auto.commit': False  # You control when to commit
}

for event in kafka.stream():
    process(event)
    if batch_complete:
        kafka.commit_offsets()  # Explicit commit after processing
```

Commit Strategies:

**At-Most-Once (commit before processing)**:
```python
for record in consumer:
    consumer.commit()     # Commit first
    process(record)       # Then process
    # Risk: If processing fails, message is lost
```

**At-Least-Once (commit after processing)** - Current approach:
```python
for record in consumer:
    process(record)       # Process first
    consumer.commit()     # Then commit
    # Risk: If commit fails, message may be processed twice
```

**Exactly-Once (using transactions)**:
```python
# Requires Kafka transactions and idempotent processing
with consumer.transaction():
    for record in consumer:
        result = process(record)
        producer.send(result)
    # Commit and produce happen atomically
```

Consumer Lag: Lag occurs when your processing speed is slower than the message production rate. In our case, the step when S3 upload happens, it would've caused a spike in lag.
```
Message Production Rate: 1000 msgs/second
Your Processing Rate:    800 msgs/second
                        ────────────────
Net Lag Increase:       200 msgs/second
```

I think we have touched upon most of the concepts related to the Kafka consumer, and now we can easily connect the dots which led to the MAX_POLL_EXCEEDED error and possible fixes.

Error: 
```
KafkaError{code=_MAX_POLL_EXCEEDED,val=-147,str="Application maximum poll interval (300000ms) exceeded by 249ms"}
```

The error means: "Consumer didn't call `poll()` for more than 5 minutes and 249 milliseconds, so it's being removed from the consumer group."

The error happened because of a processing logic blocking the polling loop:

```python
# Problematic code pattern
for event, error in kafka.stream():  # This calls poll() internally
    if event:
        self.buffer_data(event)  # Fast operation
        
        if self.should_flush():
            # This is the likely problem: blocking operation
            self.close_file_and_reset_buffer()  # Includes S3 upload (6+ minutes)
            kafka.commit_offsets()
            # poll() can't be called during S3 upload!
```

If it's hypothesized, then the most likely scenario is: 

```
Timeline of MAX_POLL_EXCEEDED Error:

0:00:00 ├─ poll() called, message received
0:00:00 ├─ buffer_data() - fast
0:00:01 ├─ poll() called, message received  
0:00:01 ├─ buffer_data() - fast
        │   ... (many messages processed quickly)
0:02:30 ├─ poll() called, message received
0:02:30 ├─ buffer_data() - fast
0:02:30 ├─ Buffer full! Start S3 upload...
0:02:30 ├─ ████████████ S3 UPLOAD (6 minutes) ████████████
        │   │
        │   │ During this time:
        │   │ - No poll() calls can happen
        │   │ - Heartbeats continue (good)
        │   │ - But max.poll.interval.ms timer keeps ticking
        │   │
0:08:30 ├─ ████████████████████████████████████████████████
0:08:30 ├─ S3 upload completes
0:08:30 ├─ commit_offsets() called
0:08:30 ├─ Try to call poll() again... ERROR!
        │
        └─ 6 minutes > 5 minute limit = MAX_POLL_EXCEEDED
```

Possible solutions would've been: 

- Increase the Timeout. We could relax a lot of other configs as well to handle other scenarios. List of configurations for [reference](https://github.com/confluentinc/librdkafka/blob/master/CONFIGURATION.md).
```python
config = {
    'max.poll.interval.ms': 900000  # 15 minutes
}
```

- Asynchronous Processing of S3 upload
```python
import concurrent.futures
class KafkaToS3Consumer:
    def __init__(self):
        self.s3_executor = concurrent.futures.ThreadPoolExecutor(max_workers=5)
    def close_file_and_reset_buffer(self):
        # Submit S3 upload to thread pool (non-blocking)
        future = self.s3_executor.submit(
            upload_to_s3, 
            self.temp_file_path
        )
        # Don't wait for completion - polling can continue
        return future
```

- Reducing the batch size of messages to be uploaded to S3.

---------------------------------------
