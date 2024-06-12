import pathlib

STATE_FILE = 'state.yaml'

def get_state_path():
    return get_root() + "/../" + STATE_FILE

def get_default_chart_path(chart):
    return get_root() + "/../charts/" + chart

def get_root():
    return str(pathlib.Path(__file__).parent.absolute())