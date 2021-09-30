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

request_file = "post.yaml"

state = StateConfig(ROOT + "/" + STATE_FILE)
request = YamlConfig(ROOT + "/" + request_file)

r = Requester(request.get("host"))

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
