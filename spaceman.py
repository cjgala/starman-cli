import pathlib
import yaml

from config import StateConfig, YamlConfig

STATE_FILE = 'state.yaml'
ROOT = str(pathlib.Path(__file__).parent.absolute())

# ============================================================

state = StateConfig(ROOT + "/" + STATE_FILE)
print(state.get("a"))

state.write("a.b", 1)
print(state.get("a"))

state.delete("a")
print(state.get("a"))
state.delete("a")
