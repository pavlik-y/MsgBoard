- memcache value with versions of recently updated values and timestamp of last write to datastore
- scenarios:
  - Read updates
    - GetUpdatedItems(progress_marker) => {ids, progress_marker}
  - Write item
    - UpdateItem(id, version, timestamp) => success
  - Begin write updates to datastore
  - Commit write updates to datastore
- Details:
  - ReadUpdates:
    - Read entry
    - If (not found|error|failed to parse): schedule cache reconstruction and respond to client with transient error
    - Select items, read and respond to client
  - WriteItem:
    - Read entry for cas
    - If (not found|error|failed to parse): schedule cache reconstruction and respond to client with transient error
    - Update datastructure
    - cas(). if failed: retry from the very beginning with limited number of retries
  - Begin write updates to datastore:
    - Read entry for cas
    - If (not found|error|failed to parse): schedule cache reconstruction and exit with failure. At the end cache reconstruction should check if cache needs to be flushed.
    - If somebody already flushing cache then exit with failure
    - Update record with flag that write was started and time when it was started
      - If cas() failed: retry from beginning
    return success
  - Commit write updates to datastore:
    - Read entry for cas
    - If (not found|error|failed to parse): schedule cache reconstruction and exit with failure. At the end cache reconstruction should check if cache needs to be flushed.
    - Verify that my flushing marker is still present, otherwise exit with failure (cache reconstruction would have triggered flush)
    - Clear flushing marker and update persisted progress marker.
    - Write updated entry
    - If failed: retry from beginning