import argparse
import json
import pathlib
import sys
import yaml

from charts import SpaceChart, ChartRequest
from config import StateConfig, YamlConfig

STATE_FILE = 'state.yaml'
ROOT = str(pathlib.Path(__file__).parent.absolute())

# ============================================================

def compile_parameters(chart, state, args):
    params = YamlConfig()

    # Read from the chart configs
    params.merge_dict(chart.get_config())

    # Read from the current state
    params.merge_dict(state.get(""))

    # Read from the user-provided parameters
    for pair in args.param:
        split = pair.split("=")
        if len(split) != 2:
            print("Malformed parameter argument '%s', must be in the form 'key=value'" % pair)
            exit(1)
        params.set(split[0], split[1])

    return params

def update_state_from_response(state, request, response):
    # Clear values in the state
    cleanup = request.get_cleanup_values()
    if cleanup != None:
        for value in cleanup:
            state.clear(value)

    # Pull updates from response
    updates = request.extract_captured_values(response)
    state.merge_dict(updates.get(""))

def print_json(data):
    if data is not None:
        print(json.dumps(data, indent=2))

# ============================================================

arg_parser = argparse.ArgumentParser(description='A tool for submitting curls from the command-line')
arg_parser.add_argument('command', metavar='COMMAND', nargs='+')
arg_parser.add_argument('--param', '-p', metavar='KEY=VALUE', action='append', type=str, default=[],
                        help='set request-specific parameters')
arg_parser.add_argument('--verbose', '-v', action='store_true',
                        help='show the API requests being sent')
arg_parser.add_argument('--test', '-t', action='store_true',
                        help='only print the API request, don\'t submit')
args = arg_parser.parse_args()

state = StateConfig(ROOT + "/" + STATE_FILE)
chart = SpaceChart(ROOT + "/charts", state.chart)
request = chart.get_request(args.command)

host = chart.get_host()
params = compile_parameters(chart, state, args)
response = request.execute(host, params, args.verbose, args.test)

if args.test:
    exit(0)
print_json(response)
update_state_from_response(state, request, response)

state.save()
