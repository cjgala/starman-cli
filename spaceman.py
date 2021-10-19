import argparse
import json
import os.path
import pathlib
import sys
import yaml

from charts import ChartRequest
from config import StateConfig, YamlConfig
from requester import Requester

STATE_FILE = 'state.yaml'
ROOT = str(pathlib.Path(__file__).parent.absolute())

# ============================================================

def get_chart_path(state):
    return ROOT + "/charts/" + state.chart

def get_manifest(state):
    path = get_chart_path(state) + "/manifest.yaml"
    if not os.path.isfile(path):
        print("Missing manifest.yaml for chart '%s'" % state.chart)
        exit(1)
    return YamlConfig(path)

def get_chart_request(state, command):
    path = get_chart_path(state) + "/" + "/".join(command) + ".yaml"
    if not os.path.isfile(path):
        print("Unknown command: " + " ".join(command))
        exit(1)
    return ChartRequest(path)

def compile_parameters(manifest, state, args):
    params = YamlConfig()

    # Read from the manifest
    params.merge_dict(manifest.get("config"))

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

def do_request(host, request, params, verbose, test):
    client = Requester(host, verbose or test, test)
    endpoint = request.render_endpoint(params)
    headers = request.render_headers(params)

    method = request.get_method()
    if method == "GET":
        return client.get(endpoint, headers)
    elif method == "POST":
        payload = request.render_payload(params)
        return client.post(endpoint, headers, payload)
    elif method == "DELETE":
        return client.delete(endpoint, headers)
    else:
        print("Unrecognized method: " + method)
        exit(1)

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

manifest = get_manifest(state)
request = get_chart_request(state, args.command)

host = manifest.get("host")
params = compile_parameters(manifest, state, args)
request.validate_params(params)

response = do_request(host, request, params, args.verbose, args.test)
if args.test:
    exit(0)

print_json(response)
update_state_from_response(state, request, response)

state.save()
