## Can client lock item with item_id
- Variables:
  - client_item_id

  - server_item_id
  - server_lock_token

  - other_item_lock_token
  - other_item_update_time

Preconditions:
client_item_id not empty
server_item_id/server_lock_token either both empty or both non-empty

Conditions:
1. server_item_id empty
2. server_item_id == client_item_id
3. IsLocked(other_item_lock_token, other_item_update_time)



If record doesn't have lock_token (1) => allow, return empty lock_token
If record has lock token and item_id matches (2) => allow and return server_lock_token

If record has lock_token, don't match item_id and the other item is locked with server_lock_token => Don't allow
else => clear server_lock_token/server_item_id, allow, return empty lock_token


- Class name matches file name: to easily locate files with implementation
- Don't import class name, instead refer to it through module name: to distinguish local and imported names
- Have variable name match class name: because variable and its class is the same concept

