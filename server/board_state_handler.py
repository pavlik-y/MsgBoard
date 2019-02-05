import collections
import time

from google.appengine.ext import ndb

import item_storage as m_item_storage
import models
import recent_updates_cache_updater
import request_status
import store_client as m_store_client

GetItemUpdatesResult = collections.namedtuple('GetItemUpdatesResult',
    ['items', 'progress_token'])
MoveResult = collections.namedtuple('MoveResult',
    ['status', 'lock_token', 'version'])
LockCheckResult = collections.namedtuple('LockCheckResult',
                                         ['can_lock', 'lock_token'])

RETRY_COUNT = 5

RecentUpdatesCacheUpdater = (
  recent_updates_cache_updater.RecentUpdatesCacheUpdater)

def ProdBoardStateHandler(board_id):
  return BoardStateHandler(m_store_client.StoreClient(board_id), board_id)

class BoardStateHandler:
  def __init__(self, store_client, board_id):
    self.store_client = store_client
    self.board_id = board_id

  def CreateBoardState(self):
    # {PAV} Should go through store_client
    board_state = models.BoardState(id = self.board_id)
    board_state.put()

  def CreateItemState(self, item_id, x, y, z):
    # {PAV} Should go through store_client
    item_state = models.ItemState(
        parent=ndb.Key(models.BoardState, self.board_id),
        id=item_id,
        x=x,
        y=y,
        z=z,
        version=1,
        update_time=time.time())
    item_state.put()

  def ConnectClient(self, client_id):
    client_entry = None
    if client_id:
      client_entry = self.store_client.ReadClientEntryDatastore(client_id)
    if client_entry is None:
      # {PAV} ClientEntryCache: Create cache entry here.
      # Implement GC for client entries.
      client_entry = models.ClientState()
      client_id = self.store_client.WriteClientEntryDatastore(client_entry)
    return client_id

  def ReadItemEntriesFromDatastore(self, progress_token_time=0.0):
    all_items = self.store_client.QueryItemsDatastore()
    items = []
    latest_update_time = 0.0
    for item in all_items:
      if item.update_time > progress_token_time:
        items.append(item)
      if latest_update_time < item.update_time:
        latest_update_time = item.update_time
    assert(latest_update_time >= progress_token_time)
    return GetItemUpdatesResult(
        items=items,
        progress_token=m_item_storage.EncodeTime(latest_update_time))

  def GetItemUpdates(self, progress_token):
    items = []
    if progress_token == None:
      result = self.ReadItemEntriesFromDatastore()
      return result
    cache_entry = self.store_client.ReadRecentUpdatesMemcacheCAS()
    if cache_entry == None:
      # {PAV} fall back to Datastore scan
      return []
    # progress_token_time = 0.0
    # if progress_token:
    #   progress_token_time = m_item_storage.DecodeTime(progress_token)

    if ShouldFallBackToFullScan(
        cache_entry.highest_uncached_time, progress_token):
      # {PAV} fall back to Datastore scan
      return []
    for item_version in cache_entry.items:
      if ShouldIncludeItemInResponse(item_version, progress_token):
        pass

    return items

  #   query = models.ItemState.query(
  #       ancestor=ndb.Key(models.BoardState, board_id))
  #   return [item for item in query]

  def CanClientLockItem_(self, item_storage, current_time,
                         client_entry, item_id):
    """
      Only called when lock_token is empty in client request. ClientEntry is
      already read from storage.
    """
    if client_entry.lock_token is None:
      return LockCheckResult(can_lock=True, lock_token=None)
    if client_entry.locked_item_id == item_id:
      return LockCheckResult(can_lock=True, lock_token=client_entry.lock_token)
    if item_storage.IsItemLockedWithToken(
        client_entry.locked_item_id, client_entry.lock_token, current_time):
      return LockCheckResult(can_lock=False, lock_token=None)
    client_entry.lock_token = None
    client_entry.locked_item_id = None
    # {PAV} ClientEntryCache. Don't forget to update
    self.store_client.WriteClientEntryDatastore(client_entry)
    return LockCheckResult(can_lock=True, lock_token=None)

  def UpdateRecentUpdatesCache_(self, item_id, item_entry, current_time):
    for _ in xrange(RETRY_COUNT):
      cache_entry = self.store_client.ReadRecentUpdatesMemcacheCAS()
      cache_updater = RecentUpdatesCacheUpdater(cache_entry)
      if not cache_updater.IsValid():
        cache_updater.Reset(current_time)
      cache_updater.RecordItem(item_id, item_entry.update_time, current_time)
      if not cache_updater.IsModified():
        return
      if self.store_client.WriteRecentUpdatesMemcache(
          cache_updater.Entry(), cache_updater.ExistedBefore()):
        # print(cache_updater.Entry())
        return

  def MoveItem(self, item_id, x, y, z, client_id, lock_token, is_release):
    now = time.time()
    item_storage = m_item_storage.ItemStorage(self.store_client, RETRY_COUNT)
    if not lock_token:
      assert(client_id is not None)
      # {PAV} Try ClientEntryCache first before hitting datastore.
      client_entry = self.store_client.ReadClientEntryDatastore(client_id)
      assert(client_entry is not None)
      lock_check_result = self.CanClientLockItem_(
          item_storage, now, client_entry, item_id)
      if not lock_check_result.can_lock:
        return MoveResult(request_status.ITEM_LOCKED, None, None)
      lock_token = lock_check_result.lock_token
    # print(lock_token, is_release)

    update_result = item_storage.LockAndUpdateItem(
        item_id, lock_token, now, is_release, x, y, z)
    if update_result.status != request_status.SUCCESS:
      return MoveResult(update_result.status, None, None)
    # Update RecentlyModified entry
    self.UpdateRecentUpdatesCache_(item_id, update_result.item_entry, now)

    if not lock_token:
      client_entry.locked_item_id = item_id
      client_entry.lock_token = update_result.item_entry.lock_token
      # {PAV} Update ClientEntryCache as well.
      self.store_client.WriteClientEntryDatastore(client_entry)
    return MoveResult(request_status.SUCCESS,
                      update_result.item_entry.lock_token,
                      update_result.item_entry.version)
