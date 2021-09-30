import argparse
import json
import pathlib
import sys
import yaml

from config import StateConfig, YamlConfig
from requester import Requester

STATE_FILE = 'state.yaml'
ROOT = str(pathlib.Path(__file__).parent.absolute())

# ============================================================

def print_json(data):
    print(json.dumps(data, indent=2))

# ============================================================

arg_parser = argparse.ArgumentParser(description='A tool for submitting curls from the command-line')
arg_parser.add_argument('command', metavar='COMMAND', nargs='+')
arg_parser.add_argument('--verbose', '-v', action='store_true', help='show the API requests being sent')
args = arg_parser.parse_args()

state = StateConfig(ROOT + "/" + STATE_FILE)
chart = state.chart

chart_path = ROOT + "/charts/" + chart
manifest = YamlConfig(chart_path + "/manifest.yaml")
r = Requester(manifest.get("host"), args.verbose)

request = YamlConfig(chart_path + "/" + args.command[0] + ".yaml")
method = request.get("method")

if method == "GET":
    result = r.get(request.get("endpoint"))
elif method == "POST":
    payload = json.loads(request.get("payload"))
    result = r.post(request.get("endpoint"), payload)
else:
    print("Unrecognized method: " + method)
    exit(1)

print_json(result)

state.save()
