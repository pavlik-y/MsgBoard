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

class ClientState(ndb.Model):
  lock_token = ndb.StringProperty('lkt')
  locked_item_id = ndb.StringProperty('lki')

# Cache
# class ItemVersion(ndb.Model):
#   item_id = ndb.StringProperty('iid')
#   version = ndb.IntegerProperty('v')
#   update_time = ndb.FloatProperty('mt')

# class UpdatedItems(ndb.Model):
#   items = ndb.StructuredProperty(ItemVersion, 'iv', repeated=True)
#   last_persisted_time_marker = ndb.FloatProperty('pt')
