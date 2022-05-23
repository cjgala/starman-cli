import os
import json
import yaml

from os.path import isfile, isdir
from spaceman.config import YamlConfig
from spaceman.render import render_template
from spaceman.requester import Requester

MANIFEST = "manifest.yaml"

def is_chart(dir_path, chart_name):
    manifest_path = dir_path + "/" + chart_name + "/" + MANIFEST
    return isfile(manifest_path)

class SpaceChart:
    def __init__(self, dir_path, chart_name, environment):
        self.name = chart_name
        self.path = dir_path + "/" + chart_name
        self.environment = environment

        manifest_path = self.path + "/" + MANIFEST
        if not isfile(manifest_path):
            print("Unable to load chart '%s'" % chart_name)
            exit(1)
        self.manifest = YamlConfig(manifest_path)

        if len(environment) > 0 and not environment in self.manifest.get("environments"):
            print("Unable to load environment '%s' for chart '%s'" % (environment, chart_name))
            exit(1)

    def print_info(self, print_yaml):
        if print_yaml:
            print("name: %s" % self.name)
            print(yaml.dump(self.manifest.data))
        else:
            print(self.name.upper())
            print("=============================")
            print(self.manifest.get("description"))
            print("\nAVAILBLE COMMANDS:")
            print("- " + "\n- ".join(self.__find_requests(self.path)))
            print("")

    def get_host(self):
        return self.manifest.get(self.__env_path("host"))

    def verify_ssl(self):
        return self.manifest.get(self.__env_path("verify_ssl"))

    def get_config(self):
        return self.manifest.get("config")

    def get_environments(self):
        return list(self.manifest.get("environments").keys())

    def get_request(self, command):
        request_path = self.path + "/" + "/".join(command) + ".yaml"
        if not isfile(request_path):
            print("Unknown command: " + " ".join(command))
            exit(1)
        return ChartRequest(" ".join(command), request_path, self)

    def __env_path(self, path):
        return "environments." + self.environment + "." + path

    def __find_requests(self, base_path):
        requests = []

        for obj in os.listdir(base_path):
            path = base_path + "/" + obj

            if isdir(path):
                dir_requests = self.__find_requests(path)
                requests += [obj + " " + request for request in dir_requests]
            elif obj == MANIFEST or obj.startswith(".") or not obj.endswith(".yaml"):
                continue
            elif isfile(path):
                requests.append(obj.removesuffix(".yaml"))

        return requests

class ChartRequest:
    def __init__(self, name, sourcefile, chart):
        self.name = name
        self.config = YamlConfig(sourcefile)
        self.payload = None
        self.chart = chart

    def print_info(self, print_yaml):
        if print_yaml:
            print("name: %s" % self.name)
            print(yaml.dump(self.config.data))
        else:
            print(self.name)
            print("=============================")
            config = self.config
            print(config.get("method") + " " + config.get("endpoint"))

            description = config.get("description")
            if description is not None:
                print(description)

            required_list = config.get("required")
            if required_list is not None:
                print("\nREQUIRED PARAMETERS:")
                print("- " + "\n- ".join([required["key"] for required in required_list]))

            optional_list = config.get("optional")
            if optional_list is not None:
                print("\nOPTIONAL PARAMETERS:")
                print("- " + "\n- ".join([optional["key"] for optional in optional_list]))
            print("")

    def execute(self, params, verbose, test):
        self.__validate_params(params)

        client = Requester(
            self.chart.get_host(),
            self.chart.verify_ssl(),
            verbose or test,
            test
        )
        endpoint = self.__render_endpoint(params)
        headers = self.__render_headers(params)

        method = self.config.get("method")
        if method == "GET":
            return client.get(endpoint, headers)
        elif method == "POST":
            payload = self.__render_payload(params)
            return client.post(endpoint, headers, payload)
        elif method == "PATCH":
            payload = self.__render_payload(params)
            return client.patch(endpoint, headers, payload)
        elif method == "DELETE":
            return client.delete(endpoint, headers)
        else:
            print("Unrecognized method: " + method)
            exit(1)

    def extract_capture_values(self, params, response):
        capture_data = YamlConfig()

        # from_request
        method = self.config.get("method")
        if method == "POST":
            request_list = self.config.get("capture.from_request")
            payload = self.__render_payload(params)
            request = json.loads(payload)
            request_data = self.__capture_from_json(request_list, params, request, "request")
            capture_data.merge_config(request_data)

        # from_response
        response_list = self.config.get("capture.from_response")
        response_data = self.__capture_from_json(response_list, params, response, "response")
        capture_data.merge_config(response_data)

        # from_config
        config_list = self.config.get("capture.from_config")
        config_data = self.__capture_from_config(config_list, params)
        capture_data.merge_config(config_data)

        return capture_data

    def get_cleanup_values(self):
        return self.config.get("cleanup")

    def __validate_params(self, params):
        required_list = self.config.get("required")
        if required_list is None:
            required_list = []

        for required in required_list:
            key = render_template(required["key"], params.get(""))
            value = params.get(key)
            if value is None:
                if "message" in required:
                    print(required["message"])
                else:
                    print("Need to provide a value for '%s'" % key)
                exit(1)
            elif "values" in required and value not in required["values"]:
                values = ", ".join(required["values"])
                print("Invalid value for '%s'\nAccepted values: %s" % (key, values))
                exit(1)

        optional_list = self.config.get("optional")
        if optional_list is None:
            optional_list = []

        for optional in optional_list:
            key = render_template(optional["key"], params.get(""))
            value = params.get(key)
            if value is None:
                continue
            elif "values" in optional and value not in optional["values"]:
                values = ", ".join(optional["values"])
                print("Invalid value for '%s'\nAccepted values: %s" % (key, values))
                exit(1)

    def __render_endpoint(self, params):
        path = render_template(self.config.get("endpoint"), params.get(""))

        parameters = self.config.get("parameters")
        if parameters is None:
            parameters = []
        request_parameters = []

        for parameter in parameters:
            value = render_template(parameter["value"], params.get(""))
            if value:
                name = parameter["name"]
                request_parameters.append("%s=%s" % (name, value))

        if len(request_parameters) > 0:
            path += "?" + "&".join(request_parameters)

        return path

    def __render_headers(self, params):
        headers = self.config.get("headers")
        render = {}
        if headers is None:
            return render

        for key in headers:
            render[key] = render_template(headers[key], params.get(""))
        return render

    def __render_payload(self, params):
        if self.payload is None:
            self.payload = render_template(self.config.get("payload"), params.get(""))
        return self.payload

    def __capture_from_json(self, capture_list, params, json, source):
        capture_data = YamlConfig()
        if capture_list is None:
            return capture_data

        for capture in capture_list:
            path = render_template(capture["path"], params.get(""))
            dest = render_template(capture["dest"], params.get(""))

            value = self.__parse_json(json, path)
            if value is None:
                print("WARNING: Unable to extract value '%s' from %s" % (path, source))
            else:
                capture_data.set(dest, value)

        return capture_data

    def __capture_from_config(self, capture_list, params):
        capture_data = YamlConfig()
        if capture_list is None:
            return capture_data

        for capture in capture_list:
            value = render_template(capture["value"], params.get(""))
            dest = render_template(capture["dest"], params.get(""))
            capture_data.set(dest, value)

        return capture_data

    def __parse_json(self, json, path):
        scope = json
        for key in path.split("."):
            if key == "":
                continue
            elif key in scope:
                scope = scope[key]
            else:
                return None
        return scope
