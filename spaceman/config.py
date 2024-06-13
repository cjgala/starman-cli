import os.path
import yaml

from spaceman.paths import get_chart_path

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
                    "path": get_chart_path("sample"),
                    "default": {}
                }
            }

        self.sourcefile = sourcefile
        self.chart = self.data["chart"]
        self.environment = self.data[self.chart]["environment"]

    def get(self, path):
        return super().get(self.__chart_path(path))

    def set(self, path, value):
        return super().set(self.__chart_path(path), value)

    def clear(self, path):
        return super().clear(self.__chart_path(path))

    def merge_dict(self, data):
        if data is not None:
            config = self.get("")
            if config is None:
                self.set("", data)
            else:
                merge_dicts(config, data)

    def get_charts(self):
        charts = list(self.data.keys())
        charts.remove("chart")
        return charts

    def get_chart_path(self, chart_name):
        data = self.data.get(chart_name)
        if data is None:
            return None
        return data.get("path")

    def add_chart(self, chart_name, chart_path, start_environment):
        if chart_name in self.data:
            return

        data = {
            "environment": start_environment,
            "path": chart_path,
            start_environment: {}
        }
        self.data[chart_name] = data

    def remove_chart(self, chart_name):
        if chart_name in self.data:
            del self.data[chart_name]

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
        base = self.chart + "." + self.environment
        return base + ("" if path == "" else "." + path)

def merge_dicts(d1, d2):
    if d2 is None:
        return
    for key in d2:
        if key in d1 and isinstance(d1[key], dict) and isinstance(d2[key], dict):
            merge_dicts(d1[key], d2[key])
        else:
            d1[key] = d2[key]
