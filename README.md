# spaceman-cli

A tool for submitting premade API requests from the command-line

```
  ____  ____   _    ____ _____ __  __    _    _   _
 / ___||  _ \ / \  / ___| ____|  \/  |  / \  | \ | |
 \___ \| |_) / _ \| |   |  _| | |\/| | / _ \ |  \| |
  ___) |  __/ ___ \ |___| |___| |  | |/ ___ \| |\  |
 |____/|_| /_/   \_\____|_____|_|  |_/_/   \_\_| \_|
```

Sometimes you want to be able to submit quick requests from the command-line, without having to look up curls in your bash history or switch to Postman to locate a request.  This is where Spaceman comes in.

Spaceman provies a series of request commands that you can exceute with a few simple keywords.  Sets of requests are managed via charts, and Spaceman allows you to easily add charts to make new request commands available.

## Using Spaceman

To see the available commands for the current chart, run `spaceman space describe`:
```
> spaceman space describe

SAMPLE
=============================
Sample chart using ReqRes API

AVAILBLE COMMANDS:
- delete
- get
- get users
- get other
- post
```
The listed commands can then be run via `spaceman COMMAND`.
```
> spaceman get

{
  "data": {
    "id": 1,
    "email": "george.bluth@reqres.in",
    "first_name": "George",
    "last_name": "Bluth",
    "avatar": "https://reqres.in/img/faces/1-image.jpg"
  },
  "support": {
    "url": "https://reqres.in/#support-heading",
    "text": "To keep ReqRes free, contributions towards server costs are appreciated!"
  }
}

```
Additional details on each command can be provided using `spaceman space describe COMMAND`.
```
> spaceman space describe get other

get other
=============================
GET /api/users/{{user_id}}
Example doing a GET request specifying a user_id

REQUIRED PARAMETERS:
- user_id
```

When describing specific command, you'll sometimes see that some commands have required parameters.  The CLI will first try to pull the parameter from the CLI state; failing that the parameter will need to be provided as part of the spaceman command.  This can be done using the `--param`/`-p` argument, followed by a key-value pair of the parameter you are trying to set.
```
> spaceman get other --param user_id=1
```

## Managing Spaceman

Besides the commands that are associated with specific charts, the CLI supports a small collection of commands to manage the CLI state (all prefixed with the `space` keyword).

For example, you can view the current CLI state with the command `spaceman space state`.
```
> spaceman space state

spaceman space state
CURRENT_CHART:		sample
CURRENT_ENVIRONMENT:	default
=============================
name: morpheus
user_id: '787'
```

**Management commands suported by the CLI**:
- `spaceman space list charts`
    - List the available charts for the CLI
- `spaceman space list environments`
    - List the available environments for the CLI 
- `spaceman space target chart CHART`
    - Select the chart the CLI should be using
- `spaceman space target environment ENV`
    - Select the environment that CLI should be using
- `spaceman space describe`
    - Describes the available commands for the current chart
    - By including the command with the request (e.g. `spaceman space describe get resource`), you can get additional details on a specific command
- `spaceman space state`
    - Presents the current CLI state, as well as the current chart and environment
        - State values that are secrets will be masked
    - Just returns the specific parameter value with `spaceman space state PARAMETER`
        - Secret state values are not masked in this case
    - Update the parameter value with `spaceman space state PARAMETER=VALUE`

## Extending Spaceman

By default the only chart Spaceman includes is the `sample` chart.  Additional charts can be added by adding dropping them into the `charts` directory of this codebase.

You can also write your own charts!  The bare minimum for a chart is a directory in the `charts` directory with a `manifest.yaml` file.  The name of the chart is based on the directory name.  The manifest file should have the following structure:
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
- `optional`: (optional) set of optional variables that can be set for the request (just for documentation)
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