SUCCESS = 0
TRANSIENT_ERROR = 1 # Too many retries
FATAL_ERROR = 2 # Persistent storage is in inconsistent state
ITEM_LOCKED = 3 # Item can't be moved as it is locked by diferent client