import os.path
import yaml

class YamlConfig:
    def __init__(self, sourcefile = None):
        if sourcefile is None:
            self.data = {}
        else:
            with open(sourcefile, "r") as stream:
                try:
                    self.data = yaml.safe_load(stream)
                except Exception as ex:
                    print(ex)
                    exit(1)

    def get(self, path):
        scope = self.data
        for key in path.split("."):
            if key == "":
                continue
            elif key in scope:
                scope = scope[key]
            else:
                return None
        return scope

    def set(self, path, value):
        keys = path.split(".")
        search_keys = keys[:-1]
        last_key = keys[-1]

        scope = self.data
        for key in search_keys:
            if key not in scope or type(scope[key]) is not dict:
                scope[key] = {}
            scope = scope[key]
        scope[last_key] = value

    def clear(self, path):
        keys = path.split(".")
        search_keys = keys[:-1]
        last_key = keys[-1]

        scope = self.data
        for key in search_keys:
            if key not in scope:
                return
            scope = scope[key]

        if last_key in scope:
            del scope[last_key]

    def merge_config(self, config):
        self.merge_dict(config.get(""))

    def merge_dict(self, data):
        if data is not None:
            merge_dicts(self.data, data)

class StateConfig(YamlConfig):
    def __init__(self, sourcefile):
        if os.path.isfile(sourcefile):
            super().__init__(sourcefile)
        else:
            self.data = {
                "chart": "sample",
                "sample": {
                    "environment": "default",
                    "default": {}
                }
            }

        self.sourcefile = sourcefile
        self.chart = self.data["chart"]
        if self.data[self.chart] == None:
            self.data[self.chart] = { "environment": "default", "default": {} }

        self.environment = self.data[self.chart]["environment"]
        if self.get("") == None:
            self.set("", {})

    def get(self, path):
        return super().get(self.__chart_path(path))

    def set(self, path, value):
        return super().set(self.__chart_path(path), value)

    def clear(self, path):
        return super().clear(self.__chart_path(path))

    def merge_dict(self, data):
        if data is not None:
            merge_dicts(self.get(""), data)

    def set_chart(self, value):
        self.chart = value
        self.data["chart"] = value

    def set_environment(self, value):
        self.environment = value
        self.data[self.chart]["environment"] = value

    def save(self):
        with open(self.sourcefile, "w") as stream:
            yaml.dump(self.data, stream)

    def __chart_path(self, path):
        return self.chart + "." + self.environment + "." + path

def merge_dicts(d1, d2):
    for key in d2:
        if key in d1 and isinstance(d1[key], dict) and isinstance(d2[key], dict):
            merge_dicts(d1[key], d2[key])
        else:
            d1[key] = d2[key]
