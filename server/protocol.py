from endpoints import messages


class CreateBoardRequest(messages.Message):
  board_id = messages.StringField(1)

class CreateItemRequest(messages.Message):
  board_id = messages.StringField(1)
  item_id = messages.StringField(2)
  x = messages.IntegerField(3)
  y = messages.IntegerField(4)
  z = messages.IntegerField(5)

class ConnectRequest(messages.Message):
  board_id = messages.StringField(1)
  client_id = messages.StringField(2)

class ConnectResponse(messages.Message):
  client_id = messages.StringField(1)
  error = messages.IntegerField(2)

class GetStateRequest(messages.Message):
  board_id = messages.StringField(1)
  version_token = messages.StringField(2)

class ItemState(messages.Message):
  id = messages.StringField(1)
  x = messages.IntegerField(2)
  y = messages.IntegerField(3)
  z = messages.IntegerField(4)
  version = messages.IntegerField(5)

class GetStateResponse(messages.Message):
  version_token = messages.StringField(1)
  items = messages.MessageField(ItemState, 2, repeated=True)

class MoveRequest(messages.Message):
  client_key = messages.StringField(1)
  board_id = messages.StringField(2)
  item_id = messages.StringField(3)
  x = messages.IntegerField(4)
  y = messages.IntegerField(5)
  z = messages.IntegerField(6)
  client_id = messages.StringField(7)
  lock_token = messages.StringField(8)
  is_release = messages.BooleanField(9, default=False)

class MoveResponse(messages.Message):
  lock_token = messages.StringField(1)
  error = messages.IntegerField(2)


class EmptyRequest(messages.Message):
  pass

class GenericResponse(messages.Message):
  pass