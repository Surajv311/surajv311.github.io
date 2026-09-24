---
layout: post 
title: DB Write Protocols & Proxies
category: technicalArticles
---

> From my experience working at [GreyOrange](https://www.greyorange.com/). Refactored my article a bit with help of GPT.

I was working on a component of a golang-service that intercepted InfluxDB writes (proxy), to enforce few rules like dropping unoptimised queries, emitting query metrics, mirroring writes to Kafka, etc. As a part of exploring the service, I learned about how different databases actually receive writes under the hood. The protocol a DB uses determines everything — I have discussed the same in this article at a high level.

There are two fundamentally different classes of DB write protocols.

**Class 1: HTTP-Based Databases**

InfluxDB, Elasticsearch, and CouchDB expose plain HTTP REST endpoints. A write is an HTTP request — nothing more.

- **InfluxDB — Line Protocol over HTTP**

  You call:
  ```go
  client.WritePoint("cpu,host=web01 usage=42.3 1609459200000000000")
  ```

  The library sends:
  ```
  POST /write?db=mydb&precision=ns HTTP/1.1
  Host: localhost:8086
  Content-Type: application/octet-stream

  cpu,host=web01 usage=42.3 1609459200000000000
  ```

  The body is InfluxDB's **Line Protocol** (a plain-text format InfluxDB invented for writing time-series data — each line encodes one data point as measurement name + tags + fields + timestamp): `measurement,tag_key=tag_val field_key=field_val timestamp`. Multiple points are newline-separated in one request body. No handshake, no session negotiation, no binary encoding — just HTTP POST with a text payload.

  For reads:
  ```
  GET /query?db=mydb&q=SELECT+usage+FROM+cpu+WHERE+time+>+now()-1h HTTP/1.1
  ```
  or `POST /query` with the InfluxQL in the body.

- **Elasticsearch — JSON over HTTP**

  Single document write:
  ```
  POST /my-index/_doc HTTP/1.1
  Content-Type: application/json

  {"@timestamp": "2024-01-01T00:00:00Z", "level": "error", "msg": "disk full"}
  ```

  Bulk write uses the `_bulk` API with NDJSON (Newline-Delimited JSON — each JSON object on its own line, no outer array; chosen because it lets the server stream-parse millions of records without loading the whole body into memory) — alternating action lines and document lines:
  ```
  POST /_bulk HTTP/1.1
  Content-Type: application/x-ndjson

  {"index": {"_index": "logs"}}
  {"level": "error", "msg": "disk full"}
  {"index": {"_index": "logs"}}
  {"level": "warn", "msg": "cpu high"}
  ```

  The library serializes your objects to JSON, adds action metadata lines, and POSTs the NDJSON body. Under the hood: just HTTP.

- **CouchDB — REST + JSON**

  ```
  PUT /mydb/doc-id HTTP/1.1
  Content-Type: application/json

  {"key": "value", "_rev": "1-abc"}
  ```

  CouchDB is perhaps the purest HTTP DB — every document operation maps directly to an HTTP verb on a URL. No special client library needed; `curl` works fine.

**Class 2: TCP Wire Protocol Databases**

Postgres, MySQL, Redis, and MongoDB do not use HTTP. They define their own binary (or text) framing over a raw TCP socket. When your application writes, the driver opens a TCP connection and speaks the DB's private protocol directly.

- **PostgreSQL — Frontend/Backend Protocol (v3)**

  Postgres defines its own binary protocol (called "Frontend/Backend Protocol" — frontend = client, backend = DB server) for communication over TCP. Each message is `[1-byte type][4-byte length][payload]`. After a startup + auth handshake, a write looks like:

  ```
  'Q'                         -- message type: Simple Query
  00 00 00 21                 -- message length (33 bytes including length itself)
  49 4E 53 45 52 54 20 49 4E 54 4F 20 74 20 56 41 4C 55 45 53 20 28 31 29 00
  -- "INSERT INTO t VALUES (1)\0"  (null-terminated SQL string)
  ```

  Server responds with `CommandComplete` (`C`, e.g., `INSERT 0 1`) and the connection stays open for the next query.

  For prepared statements, the driver splits this into three messages — Parse (send the SQL template), Bind (send the parameter values), Execute (run it). This is how `$1`, `$2` placeholders work: the SQL and the values travel separately.

- **MySQL — Client/Server Protocol**

  MySQL uses a 4-byte header per packet: 3 bytes payload length + 1 byte sequence number.

  After a handshake, writes go via `COM_QUERY` (`COM_` prefix is MySQL's naming convention for client commands; `QUERY` means "execute this SQL string" — command byte `0x03` identifies it in the binary packet):
  ```
  [payload_length 3B][sequence 1B][0x03][SQL bytes in UTF-8]
  ```

  For example, `INSERT INTO t VALUES (1)`:
  ```
  19 00 00    -- payload length: 25 bytes (1 command byte + 24 SQL bytes)
  00          -- sequence: 0
  03          -- COM_QUERY
  49 4E 53 45 52 54 20 49 4E 54 4F 20 74 20 56 41 4C 55 45 53 20 28 31 29
  ```

  For prepared statements: `COM_STMT_PREPARE` + `COM_STMT_EXECUTE`, where parameters are sent as binary-encoded typed values separately from the SQL template.

- **Redis — RESP (Redis Serialization Protocol)**

  Redis is a TCP wire-protocol DB, but unlike Postgres/MySQL its protocol is text-based, not binary. RESP (the format Redis invented for client-server communication — simple, human-readable, easy to parse line by line) looks like this:
  ```
  *3\r\n          -- array of 3 elements
  $3\r\n          -- bulk string, 3 bytes
  SET\r\n
  $5\r\n          -- bulk string, 5 bytes
  mykey\r\n
  $7\r\n          -- bulk string, 7 bytes
  myvalue\r\n
  ```

  Every Redis command is sent as a RESP array where the first element is the command name. The client library serializes `client.Set("mykey", "myvalue")` into exactly this text and writes it to the TCP socket. RESP3 (Redis 6+) adds typed responses (maps, sets, doubles) but the request framing is the same.

- **MongoDB — Wire Protocol (OP_MSG + BSON)**

  MongoDB's wire protocol wraps BSON (Binary JSON) in a message envelope: `[total_length 4B][opcode 4B][payload]` (plus some bookkeeping fields). Since MongoDB 3.6, the primary opcode is `OP_MSG` (opcode `2013` — `OP_MSG` is the unified message type that replaced the older separate `OP_INSERT`, `OP_UPDATE`, `OP_DELETE` opcodes; all operations now go through this one envelope). An insert looks like:
  ```
  OP_MSG flags (4 bytes)
  Section kind=0 (body document in BSON):
    {
      "insert": "mycollection",
      "ordered": true,
      "documents": [{"_id": ObjectId("..."), "field": "value"}],
      "$db": "mydb"
    }
  ```

  The driver serializes your document to BSON (Binary JSON — MongoDB's binary encoding of JSON-like documents; each field has a type tag byte followed by the value in binary. An integer is stored as 4 raw bytes, not ASCII digits like `"42"`. Compact, fast to parse, but not human-readable), wraps it in an `OP_MSG` body section, and writes the envelope to the TCP socket.

**Why the Protocol Matters**

| DB | Transport | Body encoding | Query/command in |
|----|-----------|---------------|-----------------|
| InfluxDB | HTTP | Line Protocol (text) | URL param `?q=` or body |
| Elasticsearch | HTTP | JSON / NDJSON | JSON body |
| CouchDB | HTTP | JSON | URL path + JSON body |
| PostgreSQL | TCP | Binary frames | `Q` message payload (text SQL) |
| MySQL | TCP | Binary frames | `COM_QUERY` payload (text SQL) |
| Redis | TCP | RESP (text arrays) | First element of RESP array |
| MongoDB | TCP | Binary frames + BSON | BSON document body |

This also determines how hard it is to debug:
- HTTP-based DBs: `tcpdump` or Wireshark gives you readable traffic immediately.
- TCP wire protocol DBs: you see binary bytes — you need a protocol dissector (Wireshark has Postgres and MySQL dissectors built in) or run the DB in verbose logging mode.

**If You Were to Build a Proxy in Front of These DBs**

- **HTTP-Based DBs (InfluxDB, ES, CouchDB)**

  Straightforward — your proxy is just an HTTP server with a forwarding client. You intercept the request, read the body, inspect/filter, then forward or reject.

  InfluxDB write interception example:
  ```go
  http.HandleFunc("/write", func(w http.ResponseWriter, r *http.Request) {
      body, _ := io.ReadAll(r.Body)
      
      for _, line := range bytes.Split(body, []byte("\n")) {
          measurement := extractMeasurement(line) // everything before first comma or space
          if isBlocked(measurement) {
              http.Error(w, "measurement blocked", http.StatusForbidden)
              return
          }
      }
      
      resp, _ := http.Post(influxAddr+"/write?"+r.URL.RawQuery,
          r.Header.Get("Content-Type"), bytes.NewReader(body))
      io.Copy(w, resp.Body)
  })
  ```

  For query filtering, parse with the official InfluxQL library — gives you an AST to inspect `WHERE` clauses, time ranges, measurements, etc.:
  ```go
  import "github.com/influxdata/influxql"

  stmt, _ := influxql.ParseStatement(queryString)
  if sel, ok := stmt.(*influxql.SelectStatement); ok {
      if sel.Condition == nil {
          return fmt.Errorf("query must have a WHERE clause")
      }
      min, max := sel.TimeRange()
      if max.Sub(min) > 35*24*time.Hour {
          return fmt.Errorf("time range too large")
      }
  }
  ```

  The standard HTTP middleware ecosystem applies — auth, rate limiting, logging, body size limits, all without touching any DB-specific code.

- **TCP Wire Protocol DBs (Postgres, MySQL, Redis, MongoDB)**

  Harder. Your proxy opens two TCP connections (client-side and server-side) and pipes bytes between them — but must parse the stream to actually read queries.

  Redis is easiest since RESP is text:
  ```go
  func parseRESP(r *bufio.Reader) ([]string, error) {
      line, _ := r.ReadString('\n')
      count, _ := strconv.Atoi(strings.TrimSpace(line[1:])) // line is "*N\r\n"
      
      args := make([]string, count)
      for i := 0; i < count; i++ {
          r.ReadString('\n')                 // "$N\r\n"
          val, _ := r.ReadString('\n')
          r.ReadString('\n')                 // trailing "\r\n"
          args[i] = strings.TrimSpace(val)
      }
      return args, nil
  }
  // args[0] = "SET", args[1] = "mykey", args[2] = "myvalue"
  // Block FLUSHDB, FLUSHALL, DEBUG etc. by checking args[0]
  ```

  Postgres requires parsing binary message framing:
  ```go
  func readPgMessage(conn net.Conn) (msgType byte, payload []byte, err error) {
      header := make([]byte, 5)
      io.ReadFull(conn, header)
      msgType = header[0]
      length := int(binary.BigEndian.Uint32(header[1:])) - 4
      payload = make([]byte, length)
      io.ReadFull(conn, payload)
      return
  }

  msgType, payload, _ := readPgMessage(clientConn)
  if msgType == 'Q' {
      sql := string(payload[:len(payload)-1]) // strip null terminator
      if violatesPolicy(sql) {
          sendPgError(clientConn, "query not allowed")
          continue
      }
  }
  writeToDBConn(dbConn, msgType, payload)
  relayResponse(dbConn, clientConn)
  ```

  For production, don't write the protocol parser from scratch — use existing libraries:
  - Postgres: `jackc/pgproto3` (Go) — full Frontend/Backend protocol implementation
  - MySQL: `go-mysql-org/go-mysql` (Go)
  - MongoDB: `mongodb/mongo-go-driver` internals, or `mongonet`
  - Redis: RESP is simple enough to write inline; `tidwall/redcon` if you need a full Redis server framework

- **What you can enforce at proxy level once you can read queries**

  - Reject queries missing a time filter / WHERE clause
  - Rate limit per client IP or per measurement/collection
  - Block specific commands or statements (FLUSHDB, DROP, DELETE without WHERE)
  - Restrict access to specific measurements / indexes / collections
  - Cost estimation before execution — run `EXPLAIN` first, reject if estimated rows exceed threshold (adds one extra round-trip but catches expensive queries that look innocent in text)

**The Core Insight**

HTTP-based DBs are just web services with domain-specific body formats. Any standard HTTP middleware — reverse proxies, API gateways, service meshes — can sit in front of them and inspect traffic without knowing anything about the DB.

TCP wire protocol DBs speak their own language. A proxy must implement or embed a parser for that binary protocol before it can read a single query. The upside: once you've parsed the framing, the query is just a string and the same filtering logic applies as for HTTP DBs.

The filtering logic itself — time bounds, rate limits, blocklists, cost estimation — is identical for both classes. The only difference is how much work you do to get the query into a readable form in the first place.

-----------------------------------------
