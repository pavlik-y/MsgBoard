import requests

local_server = 'http://localhost:8080/_ah/api/'

class MsgBoardClient:
  def __init__(self, host):
    self.host = host

  def SendRequest(self, path, request = {}):
    url = self.host + path
    r = requests.post(url, json=request)
    r.raise_for_status()
    assert(r.ok)
    return r.json()

  def CreateBoard(self, board_id):
    return self.SendRequest(
      'msgboard/v1/admin/create-board',
      {'board_id': board_id})

  def CreateItem(self, board_id, item_id, x, y, z):
    return self.SendRequest(
      'msgboard/v1/admin/create-item',
      {
        'board_id': board_id,
        'item_id': item_id,
        'x': x,
        'y': y,
        'z': z,
      })

  def DeleteBoard(self):
    return self.SendRequest('msgboard/v1/admin/delete-board')

  def GetUpdates(self, board_id):
    return self.SendRequest('msgboard/v1/state/updates',
    {
      'board_id': board_id
    })

  def ConnectClient(self, board_id, client_id):
    request = {
      'board_id': board_id,
    }
    if client_id:
      request['client_id'] = client_id
    return self.SendRequest('msgboard/v1/state/connect', request)

  def MoveItem(self, board_id, item_id, x, y, z,
               client_id = None, lock_token = None, is_release = False):
    request = {
      'board_id': board_id,
      'item_id': item_id,
      'x': x,
      'y': y,
      'z': z,
    }
    if client_id is not None:
      request['client_id'] = client_id
    if lock_token is not None:
      request['lock_token'] = lock_token
    if is_release:
      request['is_release'] = True
    return self.SendRequest('msgboard/v1/state/move', request)

def TestAPI():
  client = MsgBoardClient(local_server)
  client.CreateBoard('board1')
  client.CreateItem('board1', 'item1', 1,2,3)
  client.CreateItem('board1', 'item2', 5,6,7)
  response = client.ConnectClient('board1', 'ABRAAAAAAAA=')
  client_id = response['client_id']
  response = client.MoveItem('board1', 'item1', 8,9,10, client_id=client_id)
  print(response)
  lock_token = response['lock_token']
  response = client.MoveItem('board1', 'item1', 8,9,10, lock_token=lock_token)
  print(response)
  response = client.MoveItem('board1', 'item1', 8,9,10,
      lock_token=lock_token, is_release=True)
  print(response)
  # updates = client.GetUpdates('board1')
  # print(updates)
  # client.DeleteBoard()

def main():
  TestAPI()

if __name__ == '__main__':
  main()