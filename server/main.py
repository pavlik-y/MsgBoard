import endpoints

import board_state_handler as bsh
import protocol
import request_status

api_collection = endpoints.api(name='msgboard', version='v1')

@api_collection.api_class(resource_name='admin', path='admin')
class AdminApi(endpoints.remote.Service):
  @endpoints.method(
    protocol.CreateBoardRequest,
    protocol.GenericResponse,
    path='create-board',
    http_method='POST',
    name='createBoard')
  def CreateBoard(self, request):
    bsh.ProdBoardStateHandler(request.board_id).CreateBoardState()
    return protocol.GenericResponse()

  @endpoints.method(
    protocol.CreateItemRequest,
    protocol.GenericResponse,
    path='create-item',
    http_method='POST',
    name='createItem')
  def CreateItem(self, request):
    bsh.ProdBoardStateHandler(request.board_id).CreateItemState(
        request.item_id, request.x, request.y, request.z)
    return protocol.GenericResponse()

  @endpoints.method(
    protocol.EmptyRequest,
    protocol.GenericResponse,
    path='delete-board',
    http_method='POST',
    name='deleteBoard')
  def DeleteBoard(self, request):
    return protocol.GenericResponse()


@api_collection.api_class(resource_name='state', path='state')
class MsgBoardStateApi(endpoints.remote.Service):
  @endpoints.method(
    protocol.ConnectRequest,
    protocol.ConnectResponse,
    path='connect',
    http_method='POST',
    name='connect')
  def Connect(self, request):
    client_id = bsh.ProdBoardStateHandler(request.board_id).ConnectClient(
        request.client_id)

    return protocol.ConnectResponse(client_id=client_id)

  @endpoints.method(
    protocol.GetStateRequest,
    protocol.GetStateResponse,
    path='updates',
    http_method='POST',
    name='getUpdates')
  def GetUpdates(self, request):
    items = bsh.ProdBoardStateHandler(request.board_id).GetItemUpdates()
    items = [
        protocol.ItemState(
          id=item.key.id(),
          x=item.x, y=item.y, z=item.z,
          version=item.version)
        for item in items]
    return protocol.GetStateResponse(version_token="42", items=items)

  @endpoints.method(
    protocol.MoveRequest,
    protocol.MoveResponse,
    path='move',
    http_method='POST',
    name='moveItem')
  def MoveItem(self, request):
    result = bsh.ProdBoardStateHandler(request.board_id).MoveItem(
        request.item_id,
        request.x,
        request.y,
        request.z,
        request.client_id,
        request.lock_token,
        request.is_release,
    )
    if result.status != request_status.SUCCESS:
      response = protocol.MoveResponse(error=result.status)
    else:
      response = protocol.MoveResponse(lock_token=result.lock_token)
    return response


api = endpoints.api_server([api_collection])
