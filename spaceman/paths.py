import pathlib

STATE_FILE = 'state.yaml'
CHARTS_DIR = 'charts'

def get_state_path():
    return get_root() + "/../" + STATE_FILE

def get_charts_path():
    return get_root() + "/../" + CHARTS_DIR

def get_root():
    return str(pathlib.Path(__file__).parent.absolute())