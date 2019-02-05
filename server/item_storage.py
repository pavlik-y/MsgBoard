import base64
import collections
import struct
import time

import request_status

UpdateResult = collections.namedtuple('UpdateResult', ['status', 'item_entry'])

ITEM_LEASE_TIME = 60.0
PERSIST_INTERVAL = 5.0

def EncodeTime(time):
  return base64.b64encode(struct.pack('!d', time))

def DecodeTime(time_str):
  return struct.unpack('!d', base64.b64decode(time_str))[0]

class ItemStorage:
  def __init__(self, store_client, retry_count):
    self.store_client = store_client
    self.retry_count = retry_count

  def CanLockItem_(self, item_entry, lock_token, current_time):
    item_locked = (item_entry.lock_token and
        current_time - item_entry.update_time < ITEM_LEASE_TIME)
    if not item_locked and not lock_token:
      return True
    if item_locked and lock_token == item_entry.lock_token:
      return True
    return False

  def UpdateItemEntry_(self, item_entry, lock_token, is_release, current_time,
                       x, y, z):
    item_entry.x = x
    item_entry.y = y
    item_entry.z = z
    item_entry.update_time = current_time
    item_entry.lock_token = None if is_release else lock_token
    item_entry.version += 1

  def GenerateLockToken_(self, current_time):
    return 'lt:'+EncodeTime(current_time)

  def NeedToPersistItemEntry_(self, item_entry, current_time):
    if item_entry.lock_token == None or item_entry.persist_time == None:
      return True
    if current_time >= item_entry.persist_time + PERSIST_INTERVAL:
      return True
    # {PAV} For now all writes go through to datastore
    return True
    # return False

  # http://www.plantuml.com/plantuml/png/LP1DRiCW48NtdE8jdIlKgfGeg-wgD3q0Wh6C2eF5Z5NvziN6LSkEd_VD--0gQekkAPfZOGejPDM42SCpPoJB6mff2IGNw4ni0D6y668V9lFo8EinbPpWh9jfFCZtGaAi2DnE6uc1ywNY_nXlrTPffNB0Jihg78dqmDa8j4wAGXYsAdHAxE3TCc9sNmXAgSCxtS-bLj8H0h6MhGc_xVlbppfHwiHhsM5U4sjKlE9--nXF4SxzrStxyQnhdudlESGQVBH44Fo-qXngrnfUK_m1
  def LockAndUpdateItem(
      self, item_id, lock_token, current_time, is_release, x, y, z):
    for _ in xrange(self.retry_count):
      item_entry = self.store_client.ReadItemMemcacheForCAS(item_id)
      # print(item_entry)
      present_in_memcache = (item_entry != None)
      if not item_entry:
        item_entry = self.store_client.ReadItemDatastore(item_id)
      if not item_entry:
        # Board state is broken. Requires admin actions
        return UpdateResult(request_status.FATAL_ERROR, None)
      if not self.CanLockItem_(item_entry, lock_token, current_time):
        return UpdateResult(request_status.ITEM_LOCKED, None)
      if not lock_token:
        lock_token = self.GenerateLockToken_(current_time)
      self.UpdateItemEntry_(item_entry, lock_token, is_release, current_time,
                            x, y, z)
      # print(item_entry)
      need_to_persist = False
      if self.NeedToPersistItemEntry_(item_entry, current_time):
        item_entry.persist_time = (
            None if item_entry.lock_token == None else current_time)
        need_to_persist = True
      if not self.store_client.WriteItemMemcache(
          item_id, item_entry, present_in_memcache):
        continue
      if need_to_persist:
        self.store_client.WriteItemDatastore(item_entry)
      return UpdateResult(request_status.SUCCESS, item_entry)
    return UpdateResult(request_status.TRANSIENT_ERROR, None)

  def IsItemLockedWithToken(self, item_id, lock_token, current_time):
    item_entry = self.store_client.ReadItemMemcacheForCAS(item_id)
    # {PAV} Implement
    pass
