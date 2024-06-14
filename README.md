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

## Setting Up Spaceman

Spaceman is run using Python (3.5+).

### Setup with `pip install`

The easiest way to set up the CLI is to run:
```
pip install spaceman-cli
```

### Setup with source code

Alternatively the CLI can be executed by pulling the source code and creating an alias on `spaceman/cli.py`, e.g.
```
alias spaceman="python ~/Code/spaceman-cli/spaceman/cli.py
```
Required packages may need to be installed:
```
pip install -r requirements.txt
```
To address any SSL configuration issues:
```
pip config set global.trusted-host "pypi.org files.pythonhosted.org pypi.python.org"
```

## Using Spaceman

To see the available commands for the current chart, run `spaceman space describe`:
```
> spaceman space describe

SAMPLE
=============================
Sample chart using ReqRes API

AVAILABLE COMMANDS:
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

It's also possible to set / replace the payload used for requests, using the `--data`/`-d` argument.
```
> spaceman post --data @data.json
```
If the provided argument value starts with `@`, the CLI will assume the value is a filepath and will use its contents for the payload. Otherwise the value itself will be used for the payload.  Some requests may require the payload to be set in order to execute.

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
- `spaceman space add chart CHART PATH`
    - Add a chart to be tracked by the CLI
- `spaceman space remove chart CHART`
    - Remove a tracked chart; this will clear any state values for the chart
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

By default the only chart Spaceman includes is the `sample` chart.  Additional charts can be added by running the `spaceman space add chart` command.

You can also write your own charts!  More information can be found [here](charts.md).
