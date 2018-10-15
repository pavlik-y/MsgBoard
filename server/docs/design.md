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
  - Each update triggers several read requests.
  - Datastore handles about one request per item per second.
Consequences:
  - I cannot atomically update progress marker. Will need to use timestamp (time.time()) as a progress marker.
  - To distinguish updates I need to track per item version.
  - I need to introduce memory cache in front of datastore.
  - Cache is source of truth, periodically gets persisted to datastore.
High level blocks:
  - protocol: datastructures for client requests responses
  - api: Layer to handle/route client requests. Translates protocol to internal datastructures
  - model: datastructures for persistence in datastore and memcache

Scenarios to cover:
  - GetUpdates response size optimization
  - Push notifications and client tracking
  - Locking restrictions logic
  - Delayed flush to datastore
  - Resources
