import json

from os.path import isfile

def load_data(data_arg):
    if data_arg is None:
        return None

    is_file_data = data_arg.startswith("@")
    data = load_from_file(data_arg[1:]) if is_file_data else data_arg

    try:
       # Attempt to format the data string if json
       data_json = json.loads(data)
       return json.dumps(data_json, indent=2)
    except ValueError:
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
