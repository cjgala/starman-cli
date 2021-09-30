import json
import pathlib
import yaml

from config import StateConfig, YamlConfig
from requester import Requester

STATE_FILE = 'state.yaml'
ROOT = str(pathlib.Path(__file__).parent.absolute())

# ============================================================

def print_json(data):
    print(json.dumps(data, indent=2))

# ============================================================


state = StateConfig(ROOT + "/" + STATE_FILE)
chart = state.chart

chart_path = ROOT + "/charts/" + chart
manifest = YamlConfig(chart_path + "/manifest.yaml")
r = Requester(manifest.get("host"))

command = "get"
request = YamlConfig(chart_path + "/" + command + ".yaml")
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
