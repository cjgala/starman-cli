# Creating Charts

## Basic Structure

The bare minimum for a chart is a directory in the `charts` directory with a `manifest.yaml` file.  The name of the chart is based on the directory name.  The manifest file should have the following structure:
```yaml
description: "Sample chart using ReqRes API"
environments:
  default:
    host: https://reqres.in
    verify_ssl: true
config:
  data1: value1
  nested:
    data2: value2
secrets:
  - password
```
- `description`: some descriptive message for the chart
- `environments`: list of environments to submit requests against
    - `{name}`: name of the environment
        - `host`: host for the environment
        - `verify_ssl`: (optional) do ssl verification on the request, true by default
- `config`: (optional) set of global values to reference in the chart requests
- `secrets`: (optional) list of state values that should be masked for `spaceman space state`

## Defining Requests

Requests are represented as yaml files in the chart directory.  The CLI command for the request is based on the filename and any subdirectories.  For example, see the following directory tree:
```
get.yaml
get
└── users.yaml
```
This will make the requests `get` and `get users` available.

Request files have the following structure:
```yaml
method: POST
endpoint: /api/user
description: "Create a new user"
headers:
    Authorization: Bearer {{auth_token}}
    Content-Type: application/json
required:
  - key: auth_token
    message: Need to provide an authentication token
optional:
  - key: leader.name
payload: >
  {
    "name": "{{ leader.name | default("morpheus", true) }}",
    "job": "leader"
  }
cleanup:
  - user_id
capture:
  from_request:
    - path: name
      dest: name
  from_response:
    - path: id
      dest: user_id
```
- `method`: HTTP method for the request
- `endpoint`: endpoint for
- `description`: some description for the API request
- `headers`: (optional) set of key value pairs for headers that should be set as part of the request
- `required`: (optional) set of variables that must be either set via state or CLI parameter
    - `key`: name of the variable
    - `message`: (optional) custom message to return if the variable isn't set
    - `values`: (optional) array of accepted string values for the variable (for enums)
- `optional`: (optional) set of optional variables that can be set for the request
    - `key`: name of the variable
    - `values`: (optional) array of accepted string values for the variable (for enums)
- `parameters`: (optional) set of request parameters to set in the request URL (e.g. /api/user?key=value)
    - `name`: name of the request parameter
    - `value`: (optional) value for the request parameter
- `payload`: (optional) payload to set in the request
- `cleanup`: (optional) list of state values that should be cleared on a successful request
- `capture`: (optional) set of values that should be captured and saved to state on a successful request
    - `from_request`: (optional) set of values that should be pulled from the request object
        - `path`: path of the value in the request
        - `dest`: where the value should be saved in state
    - `from_response`: (optional) set of values that should be pulled from the response object
        - `path`: path of the value in the response
        - `dest`: where the value should be saved in state
    - `from_config`: (optional) set of values that should be pulled from state / CLI parameters
        - `path`: path of the value in state / CLI parameter
        - `dest`: where the value should be saved in state

You'll notice that many of the request yaml fields use a `{{ value }}` syntax.  That's because the request file object supports templating via [Jinja](https://jinja.palletsprojects.com/en/3.1.x/).  This allows callers to manipulate the request based on available state values or CLI parameters.  The following fields support Jinja templates:
- `endpoint`
- `headers`
    - `{header}`
- `required`
    - `key`
- `optional`
    - `key`
- `parameters`
    - `value`
- `payload`
- `capture`
    - `from_request`
        - `path`
        - `dest`
    - `from_response`
        - `path`
        - `dest`
    - `from_config`
        - `path`
        - `dest`

There are also some custom commands included with the templating logic:
- `increment(key)`: takes the value at key `key` and increments by one (assumes integer value)
- `random_uuid()`: generates a random guid
- `basic_auth(username, password)`: takes values at keys `username` and `password` and builds a base64-encoded header value
