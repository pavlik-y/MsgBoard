import collections
import time

from google.appengine.ext import ndb

import item_storage as m_item_storage
import models
import request_status
import store_client as m_store_client

MoveResult = collections.namedtuple('MoveResult', ['status', 'lock_token'])
LockCheckResult = collections.namedtuple('LockCheckResult',
                                         ['can_lock', 'lock_token'])

RETRY_COUNT = 5

def ProdBoardStateHandler(board_id):
  return BoardStateHandler(m_store_client.StoreClient(board_id), board_id)

class BoardStateHandler:
  def __init__(self, store_client, board_id):
    self.store_client = store_client
    self.board_id = board_id

  def CreateBoardState(self):
    board_state = models.BoardState(id = self.board_id)
    board_state.put()

  def CreateItemState(self, item_id, x, y, z):
    item_state = models.ItemState(
        parent = ndb.Key(models.BoardState, self.board_id),
        id = item_id,
        x = x,
        y = y,
        z = z,
        version = 1,
        update_time = time.time())
    item_state.put()

  def ConnectClient(self, client_id):
    client_entry = None
    if client_id:
      client_entry = self.store_client.ReadClientEntryDatastore(client_id)
    if client_entry is None:
      client_entry = models.ClientState()
      client_id = self.store_client.WriteClientEntryDatastore(client_entry)
    return client_id


  # def GetItemUpdates(board_id):
  #   query = models.ItemState.query(
  #       ancestor=ndb.Key(models.BoardState, board_id))
  #   return [item for item in query]

  def CanClientLockItem_(self, item_storage, current_time,
                        client_entry, item_id):
    if client_entry.lock_token is None:
      return LockCheckResult(can_lock=True, lock_token=None)
    if client_entry.locked_item_id == item_id:
      return LockCheckResult(can_lock=True, lock_token=client_entry.lock_token)
    if item_storage.IsItemLockedWithToken(
        client_entry.locked_item_id, client_entry.lock_token, current_time):
      return LockCheckResult(can_lock=False, lock_token=None)
    client_entry.lock_token = None
    client_entry.locked_item_id = None
    self.store_client.WriteClientEntryDatastore(client_entry)
    return LockCheckResult(can_lock=True, lock_token=None)

  def MoveItem(self, item_id, x, y, z, client_id, lock_token, is_release):
    now = time.time()
    item_storage = m_item_storage.ItemStorage(self.store_client, RETRY_COUNT)
    if not lock_token:
      assert(client_id is not None)
      client_entry = self.store_client.ReadClientEntryDatastore(client_id)
      assert(client_entry is not None)
      lock_check_result = self.CanClientLockItem_(
          item_storage, now, client_entry, item_id)
      if not lock_check_result.can_lock:
        return MoveResult(request_status.ITEM_LOCKED, None)
      lock_token = lock_check_result.lock_token
    # print(lock_token, is_release)

    update_result = item_storage.LockAndUpdateItem(
        item_id, lock_token, now, is_release, x, y, z)
    if update_result.status != request_status.SUCCESS:
      return MoveResult(update_result.status, None)
    # Update RecentlyModified entry
    if not lock_token:
      client_entry.locked_item_id = item_id
      client_entry.lock_token = update_result.lock_token
      self.store_client.WriteClientEntryDatastore(client_entry)
    return MoveResult(request_status.SUCCESS, update_result.lock_token)
