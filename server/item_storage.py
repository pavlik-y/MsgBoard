import collections
import time

import request_status

UpdateResult = collections.namedtuple('UpdateResult', ['status', 'lock_token'])

ITEM_LEASE_TIME = 60.0

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

  def GenerateLockToken_(self):
    return 'lock_token'+str(time.time())
  # http://www.plantuml.com/plantuml/png/LP1DRiCW48NtdE8jdIlKgfGeg-wgD3q0Wh6C2eF5Z5NvziN6LSkEd_VD--0gQekkAPfZOGejPDM42SCpPoJB6mff2IGNw4ni0D6y668V9lFo8EinbPpWh9jfFCZtGaAi2DnE6uc1ywNY_nXlrTPffNB0Jihg78dqmDa8j4wAGXYsAdHAxE3TCc9sNmXAgSCxtS-bLj8H0h6MhGc_xVlbppfHwiHhsM5U4sjKlE9--nXF4SxzrStxyQnhdudlESGQVBH44Fo-qXngrnfUK_m1
  def LockAndUpdateItem(
      self, item_id, lock_token, current_time, is_release, x, y, z):
    for _ in xrange(self.retry_count):
      item_entry = self.store_client.ReadItemMemcacheForCAS(item_id)
      print(item_entry)
      present_in_memcache = (item_entry != None)
      if not item_entry:
        item_entry = self.store_client.ReadItemDatastore(item_id)
      if not item_entry:
        # Board state is broken. Requires admin actions
        return UpdateResult(request_status.FATAL_ERROR, None)
      if not self.CanLockItem_(item_entry, lock_token, current_time):
        return UpdateResult(request_status.ITEM_LOCKED, None)
      if not lock_token:
        lock_token = self.GenerateLockToken_()
      self.UpdateItemEntry_(item_entry, lock_token, is_release, current_time,
                            x, y, z)
      print(item_entry)
      if present_in_memcache:
        if not self.store_client.WriteItemMemcacheCAS(item_id, item_entry):
          continue
      else:
        if not self.store_client.AddItemMemcache(item_id, item_entry):
          continue
      return UpdateResult(request_status.SUCCESS, lock_token)
    return UpdateResult(request_status.TRANSIENT_ERROR, None) # Transient error
