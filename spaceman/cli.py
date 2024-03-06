import argparse
import json
import os
import pathlib
import yaml

from argparse import RawTextHelpFormatter
from http.client import responses
from os.path import isdir
from spaceman.charts import SpaceChart, is_chart
from spaceman.config import StateConfig, YamlConfig
from spaceman.loader import load_data
from spaceman.render import render_template

STATE_FILE = 'state.yaml'
CHARTS_DIR = 'charts'
ROOT = str(pathlib.Path(__file__).parent.absolute())
CHARTS_PATH = ROOT + "/" + CHARTS_DIR

# ============================================================

def list_info(state, args):
    if len(args.command) == 2:
        print("Please specify what you want to list\nAccepted values: charts, environments")
        exit(1)

    target = args.command[2]
    if target == "charts":
        list_charts(state, args)
    elif target == "environments" or target == "env":
        list_environments(state, args)
    else:
        print("Unrecognized value '%s'\nAccepted values: charts, environments" % target)
        exit(1)

def list_charts(state, args):
    charts = []
    for obj in os.listdir(CHARTS_PATH):
       obj_path = CHARTS_PATH + "/" + obj

       if isdir(obj_path) and is_chart(CHARTS_PATH, obj):
           charts.append(obj)

    if len(charts) == 0:
        print("No available charts")
    else:
        annotated = list(map(lambda chart: chart + " *" if chart == state.chart else chart, charts))
        print("AVAILABLE CHARTS:")
        print("- " + "\n- ".join(annotated))
        print("")

def list_environments(state, args):
    chart = SpaceChart(CHARTS_PATH, state.chart, state.environment)
    environments = chart.get_environments()

    if len(environments) == 0:
        print("No available environments")
    else:
        annotated = list(map(lambda env: env + " *" if env == state.environment else env, environments))
        print("AVAILABLE ENVIRONMENTS:")
        print("- " + "\n- ".join(annotated))
        print("")

# ============================================================

def change_target(state, args):
    if len(args.command) == 2:
        print("Please specify what you want to list\nAccepted values: charts, environments")
        exit(1)

    target = args.command[2]
    if target == "chart":
        change_chart(state, args)
    elif target == "environment" or target == "env":
        change_environment(state, args)
    else:
        print("Unrecognized value '%s'\nAccepted values: chart, environment" % target)
        exit(1)

def change_chart(state, args):
    if len(args.command) == 3:
        print("Please specify a chart you want to switch to")
        exit(1)
    new_chart = args.command[3]

    chart = SpaceChart(CHARTS_PATH, new_chart, "")
    start_environment = chart.get_environments()[0]

    state.set_chart(new_chart, start_environment)
    print("Switched to using chart '%s'" % new_chart)

def change_environment(state, args):
    if len(args.command) == 3:
        print("Please specify an environment you want to switch to")
        exit(1)
    new_env = args.command[3]

    # Test loading the chart environment to see if it's valid
    SpaceChart(CHARTS_PATH, state.chart, new_env)

    state.set_environment(new_env)
    print("Switched to using environment '%s'" % new_env)

# ============================================================

def describe_chart(state, args):
    chart = SpaceChart(CHARTS_PATH, state.chart, state.environment)

    if len(args.command) == 2:
        chart.print_info(args.yaml)
    else:
        request = chart.get_request(args.command[2:])
        request.print_info(args.yaml)

# ============================================================

def manage_state(state, args):
    if len(args.command) == 2:
        print("CURRENT_CHART:\t\t" + state.chart)
        print("CURRENT_ENVIRONMENT:\t" + state.environment)
        print("=============================")

        chart = SpaceChart(CHARTS_PATH, state.chart, state.environment)
        data = state.get("")
        if data is not None:
            masked = chart.mask_secrets(data)
            print(yaml.dump(masked))
    else:
        param = args.command[2]
        split = param.split("=")
        if len(split) < 2:
            value = state.get(split[0])
            if isinstance(value, (dict)):
                print(yaml.dump(value))
            else:
                print(value)
        else:
            key = split[0]
            value = "=".join(split[1:])
            state.set(key, value)
            print(value)

# ============================================================

def execute_request(state, args):
    chart = SpaceChart(CHARTS_PATH, state.chart, state.environment)
    request = chart.get_request(args.command)

    # Validate that the CLI params align with the chart params
    cli_params = get_cli_parameters(args)
    request.validate_cli_params(cli_params)

    # Compile all params and execute
    params = compile_parameters(chart, state, cli_params)
    data = load_data(args.data)
    response = request.execute(params, data, args.verbose, args.curl, args.test)

    if args.test or args.curl:
        exit(0)

    response.pretty_print()
    if args.verbose:
        print("%d %s\n" % (response.status, responses[response.status]))

    if response.status > 299:
        exit(3)
    elif not args.skip_update:
        update_state_from_response(state, params, data, request, response, args.verbose)

def get_cli_parameters(args):
    params = YamlConfig()

    for pair in args.param:
        split = pair.split("=")
        if len(split) != 2:
            print("Malformed parameter argument '%s', must be in the form 'key=value'" % pair)
            exit(1)
        params.set(split[0], split[1])

    return params

def compile_parameters(chart, state, cli_params):
    params = YamlConfig()

    # Read from the chart configs
    params.merge_dict(chart.get_config())

    # Read from the current state
    params.merge_config(state)

    # Read from the user-provided parameters
    params.merge_config(cli_params)

    return params

def update_state_from_response(state, params, data, request, response, verbose):
    # Clear values in the state
    cleanup = request.get_cleanup_values()
    if cleanup != None:
        for value in cleanup:
            state.clear(render_template(value, params.get("")))

    # Pull updates from response
    updates = request.extract_capture_values(params, data, response, verbose)
    state.merge_config(updates)

def print_json(data):
    if data is not None:
        print(json.dumps(data, indent=2))

# ============================================================

arg_parser = argparse.ArgumentParser(description=r"""
==========================================================================
  ____  ____   _    ____ _____ __  __    _    _   _
 / ___||  _ \ / \  / ___| ____|  \/  |  / \  | \ | |
 \___ \| |_) / _ \| |   |  _| | |\/| | / _ \ |  \| |
  ___) |  __/ ___ \ |___| |___| |  | |/ ___ \| |\  |
 |____/|_| /_/   \_\____|_____|_|  |_/_/   \_\_| \_|

A tool for submitting curls from the command-line

AVAILABLE COMMANDS:
- space list charts
- space list environments
- space target chart
- space target environment
- space describe
- space state

Additional commands for current chart can be found using 'space describe'.

==========================================================================
""", formatter_class=RawTextHelpFormatter)

arg_parser.add_argument('command', metavar='COMMAND', nargs='+')
arg_parser.add_argument('--param', '-p', metavar='KEY=VALUE', action='append', type=str, default=[],
                        help='set request-specific parameters')
arg_parser.add_argument('--data', '-d', metavar='data.json', type=str,
                        help='override data payload to submit in the request')
arg_parser.add_argument('--verbose', '-v', action='store_true',
                        help='show the API requests being sent')
arg_parser.add_argument('--curl', '-c', action='store_true',
                        help='represent the API request as a curl request')
arg_parser.add_argument('--test', '-t', action='store_true',
                        help='only print the API request, don\'t submit')
arg_parser.add_argument('--yaml', '-y', action='store_true',
                        help='when using \'space describe\', prints the raw yaml data')
arg_parser.add_argument('--skip-update', '-s', action='store_true',
                        help='don\'t update state after submitting the request')
args = arg_parser.parse_args()

# ============================================================

def main():
    state = StateConfig(ROOT + "/" + STATE_FILE)
    base_command = args.command[0]

    if base_command == "space":
        actions = {
            "list": list_info,
            "target": change_target,
            "describe": describe_chart,
            "state": manage_state
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


if __name__ == '__main__':
    main()
