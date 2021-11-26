import argparse
import json
import os
import pathlib
import sys
import yaml

from charts import SpaceChart, ChartRequest, is_chart
from config import StateConfig, YamlConfig
from os.path import isdir

STATE_FILE = 'state.yaml'
CHARTS_DIR = 'charts'
ROOT = str(pathlib.Path(__file__).parent.absolute())
CHARTS_PATH = ROOT + "/" + CHARTS_DIR

# ============================================================

def list_charts(state, args):
    charts = []
    for obj in os.listdir(CHARTS_PATH):
       obj_path = CHARTS_PATH + "/" + obj

       if isdir(obj_path) and is_chart(CHARTS_PATH, obj):
           charts.append(obj)

    if len(charts) == 0:
        print("No available charts")
    else:
        print("AVAILBLE CHARTS:")
        print("- " + "\n- ".join(charts))
        print("")

def change_chart(state, args):
    if len(args.command) == 2:
        print("Please specify a chart you want to switch to")
        exit(1)
    new_chart = args.command[2]

    # Test loading the chart to see if it's valid
    SpaceChart(CHARTS_PATH, new_chart)

    state.set_chart(new_chart)
    print("Switched to using chart '%s'" % new_chart)

def get_status(state, args):
    print("CURRENT_CHART:\t" + state.chart)
    print("")

def describe_chart(state, args):
    chart = SpaceChart(CHARTS_PATH, state.chart)

    if len(args.command) == 2:
        chart.print_info(args.config)
    else:
        request = chart.get_request(args.command[2:])
        request.print_info(args.config)

# ============================================================

def execute_request(state, args):
    chart = SpaceChart(ROOT + "/" + CHARTS_DIR, state.chart)
    request = chart.get_request(args.command)

    host = chart.get_host()
    params = compile_parameters(chart, state, args)
    response = request.execute(host, params, args.verbose, args.test)

    if args.test:
        exit(0)
    print_json(response)
    update_state_from_response(state, request, response)

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
arg_parser.add_argument('--config', '-c', action='store_true',
                        help='when using \'space describe\', prints the raw yaml config')
args = arg_parser.parse_args()

# ============================================================

state = StateConfig(ROOT + "/" + STATE_FILE)
base_command = args.command[0]

if base_command == "space":
    actions = {
        "list": list_charts,
        "target": change_chart,
        "describe": describe_chart,
        "status": get_status
    }

    if len(args.command) == 1:
        print("Please specify a subcommand you want to use")
        print("Available subcommands: " + ", ".join(actions.keys()))
        exit(1)
    if args.command[1] not in actions:
        print("Unknown command: " + " ".join(args.command))
        exit(1)

    action_command = args.command[1]
    actions[action_command](state, args)
else:
    execute_request(state, args)

state.save()
