import argparse
import json
import os.path
import pathlib
import sys
import yaml

from config import StateConfig, YamlConfig
from jinja2 import Template
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

def get_request_details(state, command):
    path = get_chart_path(state) + "/" + "/".join(command) + ".yaml"
    if not os.path.isfile(path):
        print("Unknown command: " + " ".join(command))
        exit(1)
    return YamlConfig(path)

def compile_parameters(manifest, state, args):
    params = {}

    # Read from the manifest
    if type(manifest.get("parameters")) is dict:
        params = params | manifest.get("parameters")

    # Read from the current state
    params = params | state.get("")

    # Read from the user-provided parameters
    for pair in args.param:
      split = pair.split("=")
      if len(split) != 2:
          print("Malformed parameter argument '%s', must be in the form 'key=value'" % pair)
          exit(1)
      params[split[0]] = split[1]

    return params

def make_request(host, request, params, verbose):
    r = Requester(host, verbose)
    headers = request.get("headers")
    endpoint = request.get("endpoint")

    method = request.get("method")
    if method == "GET":
        return r.get(endpoint, headers)
    elif method == "POST":
        payload = request.get("payload")
        render = Template(payload).render(params)
        return r.post(endpoint, headers, render)
    else:
        print("Unrecognized method: " + method)
        exit(1)

def print_json(data):
    print(json.dumps(data, indent=2))

# ============================================================

arg_parser = argparse.ArgumentParser(description='A tool for submitting curls from the command-line')
arg_parser.add_argument('command', metavar='COMMAND', nargs='+')
arg_parser.add_argument('--param', '-p', metavar='KEY=VALUE', action='append', type=str, default=[],
                        help='set request-specific parameters')
arg_parser.add_argument('--verbose', '-v', action='store_true',
                        help='show the API requests being sent')
args = arg_parser.parse_args()

state = StateConfig(ROOT + "/" + STATE_FILE)

manifest = get_manifest(state)
request = get_request_details(state, args.command)

host = manifest.get("host")
params = compile_parameters(manifest, state, args)

result = make_request(host, request, params, args.verbose)
print_json(result)

state.save()
