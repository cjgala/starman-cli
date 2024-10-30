import os
import pathlib

STATE_DIRECTORY = '/.starman'
STATE_FILE = '/state.yaml'
CHARTS = '/charts/'

def get_state_path():
    state_directory = str(pathlib.Path.home()) + STATE_DIRECTORY
    # Create the directory if it doesn't exist
    pathlib.Path(state_directory).mkdir(exist_ok=True)
    return state_directory + STATE_FILE

def get_chart_path(chart):
    current_directory = str(pathlib.Path(__file__).parent.absolute())
    return os.path.abspath(current_directory + CHARTS + chart)