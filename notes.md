- Setup libraries (https://cloud.google.com/endpoints/docs/frameworks/python/get-started-frameworks-python#installing_the_endpoints_frameworks_library):
  - write requirements in requirements.txt
  - mkdir lib
  - pip install --target lib --requirement requirements.txt --ignore-installed

- Generate OpenAPI document:
  - from src
  - python lib/endpoints/endpointscfg.py get_openapi_spec main.MsgBoardStateApi --hostname pavtestapp.appspot.com

- Run server locally:
  - dev_appserver.py --log_level debug app.yaml

- Send request:
  - curl --request POST --header "Content-Type: application/json" --data '' http://localhost:8080/_ah/api/msgboard/v1/state

curl --request POST --header "Content-Type: application/json" --data '' http://localhost:8080/_ah/api/echo/v1/echo

- Start pipenv:
  - pipenv shell
- Run tests:
  - python test-endpoints.py