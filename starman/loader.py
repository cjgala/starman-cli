import json

from os.path import isfile
from xml.dom.minidom import parseString as parseXmlString
from xml.parsers.expat import ExpatError

def load_request_data(data_arg):
    if data_arg is None:
        return None

    is_file_data = data_arg.startswith("@")
    data = load_from_file(data_arg[1:]) if is_file_data else data_arg

    try:
       # Attempt to format the data string if json
       data_json = json.loads(data)
       return json.dumps(data_json, indent=2)
    except ValueError:
        try:
            # Fallback to xml if that fails
            document = parseXmlString(data)
            return document.toprettyxml()
        except ExpatError:
            return data

def load_from_file(path):
    if not isfile(path):
        print("Unable to read file at path '%s'" % path)
        exit(1)

    with open(path, "r") as file:
        try:
            return file.read()
        except Exception as ex:
            print(ex)
            exit(1)
