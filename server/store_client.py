import base64
import struct

from google.appengine.api import memcache
from google.appengine.ext import ndb

import models

class StoreClient:
  def __init__(self, board_id):
    self.board_id = board_id
    self.memcache_client = memcache.Client()
  def ReadClientEntryDatastore(self, client_id):
    client_id = struct.unpack('!q', base64.b64decode(client_id))[0]
    client_entry_key = ndb.Key(models.ClientState, client_id)
    client_entry = client_entry_key.get()
    return client_entry
  def WriteClientEntryDatastore(self, client_entry):
    client_entry_key = client_entry.put()
    client_id = client_entry_key.id()
    client_id = base64.b64encode(struct.pack('!q', client_id))
    return client_id
  def ReadItemMemcacheForCAS(self, item_id):
    return self.memcache_client.get(
        key="is|"+item_id,
        namespace=self.board_id,
        for_cas=True)
  def ReadItemDatastore(self, item_id):
    item_key = ndb.Key(models.BoardState, self.board_id,
                       models.ItemState, item_id)
    item_entry = item_key.get()
    return item_entry
  def WriteItemMemcacheCAS(self, item_id, item_entry):
    return self.memcache_client.cas(
        key="is|"+item_id,
        value=item_entry,
        namespace=self.board_id)
  def AddItemMemcache(self, item_id, item_entry):
    return self.memcache_client.add(
        key="is|"+item_id,
        value=item_entry,
        namespace=self.board_id)

