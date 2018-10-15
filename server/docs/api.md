- Minimize client traffic:
  - Minimize amount of data sent in the response
  - Minimize number of requests sent to server

- Minimize amount of data:
  - To receive updates client calls GetUpdates
  - Response only includes items changed since the last time client called GetUpdates
  - To facilitate this client sends last progress marker to server
  - Server sends updated progress marker in the response

- Minimize number of requests:
  - Setup push notifications to trigger client's GetUpdates

- Real time updates:
  - Agressive GetUpdates schedule (wasted traffic)
  - Push notifications

- Moving items:
  - Client calls MoveItem
  - Server should check if the client already holds the lock th some other item and reject request. This ensures moving only one item at a time.
  - To facilitate real time updates client calls MoveItem periodically while item is being moved.
  - To facilitate "No stealing items" server locks item being moved by client. It will reject Move request by other clients
  - Client can fail, resulting in item remaining locked indefinitely. To address that server will only grant lock for an item for a limited time. Client needs to call Move periodically to maintain the lock.
  - To relase item after move client will call MoveItem with release_item set to True.

- APIs:
  - ConnectClient
    - Request:
      - board_id
      - client_id
    - Response:
      - client_id
  - GetUpdates
    - Request:
      - board_id
      - progress_marker
    - Response:
      - progress_marker
      - Items
        - id
        - x, y, z
        - version
  - MoveItem
    - Request:
      - client_id
      - board_id
      - move_token
      - item_id
      - x,y,z
      - release_item (optional)
    - Response (successful):
      - move_token
      - version

- Admin APIs:
  - Delete board
    - board_id
  - CreateBoard:
    - board_id
  - CreateItem:
    - board_id
    - item_id
    - x, y, z
  - ClearCleints:
    - board_id


- Endpoints:
  - msgboard/v1
    - state
      - connect
      - updates
      - move
    - admin
      - delete-board
      - create-board
      - create-item
