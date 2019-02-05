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
  progress_token = messages.StringField(2)

class ItemState(messages.Message):
  id = messages.StringField(1)
  x = messages.IntegerField(2)
  y = messages.IntegerField(3)
  z = messages.IntegerField(4)
  version = messages.IntegerField(5)

class GetStateResponse(messages.Message):
  progress_token = messages.StringField(1)
  items = messages.MessageField(ItemState, 2, repeated=True)

class MoveRequest(messages.Message):
  board_id = messages.StringField(1)
  item_id = messages.StringField(2)
  x = messages.IntegerField(3)
  y = messages.IntegerField(4)
  z = messages.IntegerField(5)
  client_id = messages.StringField(6)
  lock_token = messages.StringField(7)
  is_release = messages.BooleanField(8, default=False)

class MoveResponse(messages.Message):
  lock_token = messages.StringField(1)
  version = messages.IntegerField(2)
  error = messages.IntegerField(3)


class EmptyRequest(messages.Message):
  pass

class GenericResponse(messages.Message):
  pass