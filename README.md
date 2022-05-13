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
- other get
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
> spaceman space describe other get

other get
=============================
GET /api/users/{{user_id}}
Example doing a GET request specifying a user_id

REQUIRED PARAMETERS:
- user_id
```

When describing specific command, you'll sometimes see that some commands have required parameters.  The CLI will first try to pull the parameter from the CLI state; failing that the parameter will need to be provided as part of the spaceman command.  This can be done using the `--param`/`-p` argument, followed by a key-value pair of the parameter you are trying to set.
```
> spaceman other get --param user_id=1
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
- `spaceamn space list environments`
    - List the available environments for the CLI 
- `spaceman space target chart`
    - Select the chart the CLI should be using
- `spaceman space target environment`
    - Select the environment that CLI should be using
- `spaceman space describe`
    - Describes the available commands for the current chart
    - By including the command with the request (e.g. `spaceman space describe get resource`), you can get additional details on a specific command.
- `spaceman space state`
    - Presents the current CLI state, as well as the current chart and environment
    - Will just return the specific parameter value by using `spaceman space state PARAMETER`
    - Will update the parameter value by using `spaceman space state PARAMETER=VALUE`

## Extending Spaceman

WIP
