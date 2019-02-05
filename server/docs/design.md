- Technologies needed:
  - Persistent storage
  - Likely cache because of lots of read requests after single update
  - Likely push notification to avoid clients constantly polling

- Technology choice:
  - Google
  - Microsoft
  - Amazon

- Constraints:
  - Clients send updates multiple times a second.
  - Each update triggers several read requests from observing clients.
  - Datastore handles about one request per second.

- Consequences:
  - I cannot atomically update progress marker. Will need to use timestamp (time.time()) as a progress marker.
  - To distinguish updates I need to track per item version.
  - I need to introduce memory cache in front of datastore.
  - Cache is source of truth, periodically gets persisted to datastore.

- High level blocks:
  - protocol: datastructures for client requests responses
  - api: Layer to handle/route client requests. Translates protocol to internal datastructures
  - model: datastructures for persistence in datastore and memcache

- Scenarios to cover:
  - GetUpdates response size optimization
  - Push notifications and client tracking
  - Locking restrictions logic
  - Delayed flush to datastore
  - Resources

- Design:
  - Each item in its own record in datastore
  - Memcache entry for each item stores patest version
  - Some of the updates from client get persisted to datastore:
    - First and last update
    - Once every N seconds (tracked in memcache entry)
  - Client's record in datastore to track locking constraints

- Reader flow considerations:
  - Worst case perform full scan from datastore
  - If client has recent progress marker then read should be served from memcache.
    - Server should translate progress marker to all items updated since then
      - There should be memcache entry with item ids of recently updated items
      - This entry should not be updated on every move as it will become contention point
      - Read codepath should assume that if the item is not released then there could have been more changes in the interval of N seconds after the last update that wasn't reflected in the cache record.
      - Cache record can be sharded. Introducing additional shards will releave contention on cache records at the cost of more reads for read flow.

- Reader flow:
  - Read memcached recent updates records.
    - For missing records fallback to datastore scan. Create empty cache record.
  - If client's progress marker is too old, fallback to datastore scan
    - We can potentially cache the response keying it on the pair (client's progress marker, latest update progress marker). This will optimize the case of many clients being behind.
  - Scan entries in recent updates cache record, determine which entries to read.
    - Introduce helper class that would encapsulate logic of when to update/read entry. The logic should be shared by reader and writer flow.
  - Read entries, falling back to datastore if needed, determine which ones to serve to client based on entry version.
