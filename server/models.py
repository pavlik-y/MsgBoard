from google.appengine.ext import ndb

class BoardState(ndb.Model):
  pass

class ItemState(ndb.Model):
  x = ndb.IntegerProperty()
  y = ndb.IntegerProperty()
  z = ndb.IntegerProperty()
  version = ndb.IntegerProperty('v')
  update_time = ndb.FloatProperty('mt')
  lock_token = ndb.StringProperty('lk')
  persist_time = ndb.FloatProperty('pt')

  @classmethod
  def query_items(cls, board_id):
    board_key = ndb.Key(BoardState, board_id)
    return cls.query(ancestor=board_key)

class ClientState(ndb.Model):
  lock_token = ndb.StringProperty('lkt')
  locked_item_id = ndb.StringProperty('lki')

# Cache
class ItemVersion(ndb.Model):
  item_id = ndb.StringProperty('iid')
  update_time = ndb.FloatProperty('mt')

class RecentUpdates(ndb.Model):
  items = ndb.StructuredProperty(ItemVersion, 'iv', repeated=True)
  highest_uncached_time = ndb.FloatProperty('hut')
  # highest_persisted_time = ndb.FloatProperty('hpt')
