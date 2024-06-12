import os
import pathlib

from os.path import isdir

STATE_DIRECTORY = '/.spaceman'
STATE_FILE = '/state.yaml'
CHARTS = 'charts'

def get_state_path():
    state_directory = str(pathlib.Path.home()) + STATE_DIRECTORY
    pathlib.Path(state_directory).mkdir(exist_ok=True)

    return state_directory + STATE_FILE

def get_default_chart_path(chart):
    root = str(pathlib.Path(__file__).parent.absolute())
    path = root + "/../" + CHARTS + "/" + chart
    return os.path.abspath(path)