import yaml

class YamlConfig:
    def __init__(self, sourcefile):
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

class StateConfig(YamlConfig):
    def __init__(self, sourcefile):
        super().__init__(sourcefile)
        self.sourcefile = sourcefile

        if "chart" not in self.data:
            self.data["chart"] = "default"
        self.chart = self.data["chart"]

    def get(self, path):
        return super().get(self.__chart_path(path))

    def write(self, path, value):
        keys = self.__chart_path(path).split(".")
        search_keys = keys[:-1]
        last_key = keys[-1]

        scope = self.data
        for key in search_keys:
            if key not in scope or type(scope[key]) is not dict:
                scope[key] = {}
            scope = scope[key]
        scope[last_key] = value

    def delete(self, path):
        keys = self.__chart_path(path).split(".")
        search_keys = keys[:-1]
        last_key = keys[-1]

        scope = self.data
        for key in search_keys:
            if key not in scope:
                return
            scope = scope[key]

        if last_key in scope:
            del scope[last_key]

    def set_chart(self, value):
        self.chart = value;

    def save(self):
        with open(self.sourcefile, "w") as stream:
            yaml.dump(self.data, stream)

    def __chart_path(self, path):
        return self.chart + "." + path
