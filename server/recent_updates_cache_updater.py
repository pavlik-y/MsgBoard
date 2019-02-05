import models

MAX_CACHE_AGE = 600.0

class RecentUpdatesCacheUpdater:
  def __init__(self, cache_entry):
    self.existed_before = (cache_entry != None)
    self.cache_entry = cache_entry
    self.is_modified = False

  def IsValid(self):
    return self.cache_entry != None

  def IsModified(self):
    return self.is_modified

  def ExistedBefore(self):
    return self.existed_before

  def Reset(self, current_time):
    self.is_modified = True
    self.cache_entry = models.RecentUpdates(highest_uncached_time=current_time)

  def Entry(self):
    return self.cache_entry

  def RecordItem(self, item_id, update_time, current_time):
    item_updated = False
    index = 0
    while index < len(self.cache_entry.items):
      item = self.cache_entry.items[index]
      if item.item_id == item_id and update_time > item.update_time:
        item.update_time = update_time
        item_updated = True
        self.is_modified = True
      if (current_time - item.update_time > MAX_CACHE_AGE):
        self.cache_entry.highest_uncached_time = max(
            self.cache_entry.highest_uncached_time, item.update_time)
        self.cache_entry.items.pop(index)
        self.is_modified = True
      else:
        index += 1
    if not item_updated:
      self.cache_entry.items.append(models.ItemVersion(
          item_id=item_id,
          update_time=update_time))
      self.is_modified = True
