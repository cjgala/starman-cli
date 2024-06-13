import copy
import os
import json
import xmltodict
import yaml

from os.path import isfile, isdir
from xml.parsers.expat import ExpatError

from spaceman.config import YamlConfig
from spaceman.render import render_template
from spaceman.requester import Requester
from spaceman.response import ResponseType

MANIFEST = "manifest.yaml"

def is_chart(dir_path, chart_name):
    manifest_path = dir_path + "/" + chart_name + "/" + MANIFEST
    return isfile(manifest_path)

class SpaceChart:
    def __init__(self, chart_path, chart_name, environment):
        self.name = chart_name
        self.path = chart_path
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
            print("\nAVAILABLE COMMANDS:")
            print("- " + "\n- ".join(self.__find_requests(self.path)))
            print("")

    def mask_secrets(self, data):
        masked = copy.copy(data)
        secrets = self.manifest.get("secrets")

        if secrets is not None:
            for key in secrets:
                if key in masked:
                    masked[key] = "****"

        return masked

    def get_host(self):
        return self.manifest.get(self.__env_path("host"))

    def verify_ssl(self):
        value = self.manifest.get(self.__env_path("verify_ssl"))
        return True if value is None else value

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

            if config.get("required_payload"):
                print("\nREQUIRED PAYLOAD: true")
            print("")

    def validate_cli_params(self, params):
        required_list = self.config.get("required")
        if required_list is None:
            required_list = []
        required_params = list(map(lambda x: x["key"], required_list))

        optional_list = self.config.get("optional")
        if optional_list is None:
            optional_list = []
        optional_params = list(map(lambda x: x["key"], optional_list))

        for param in params.data.keys():
            if param not in required_params and param not in optional_params:
                print("Unrecognized parameter '%s'" % param)
                exit(1)

    def execute(self, params, data, verbose, curl, test):
        self.__validate_params(params)

        client = Requester(
            self.chart.get_host(),
            self.chart.verify_ssl(),
            verbose or test,
            curl,
            test or curl
        )
        endpoint = self.__render_endpoint(params)
        headers = self.__render_headers(params)
        response_type = self.__get_response_type()

        method = self.config.get("method")
        if method == "GET":
            return client.get(endpoint, headers, response_type)
        elif method == "POST":
            payload = self.__render_payload(params, data)
            return client.post(endpoint, headers, payload, response_type)
        elif method == "PUT":
            payload = self.__render_payload(params, data)
            return client.put(endpoint, headers, payload, response_type)
        elif method == "PATCH":
            payload = self.__render_payload(params, data)
            return client.patch(endpoint, headers, payload, response_type)
        elif method == "DELETE":
            return client.delete(endpoint, headers, response_type)
        else:
            print("Unrecognized method: " + method)
            exit(1)

    def extract_capture_values(self, params, data, response, verbose):
        capture_data = YamlConfig()
        response_body = response.get_body()
        headers = response.headers

        # from_request
        method = self.config.get("method")
        if method in ["POST", "PUT", "PATCH"]:
            request_list = self.config.get("capture.from_request")
            payload = self.__render_payload(params, data)
            if payload:
                request = self.__load_payload(payload)
                request_data = self.__capture_from_dict(request_list, params, request, "request", verbose)
                capture_data.merge_config(request_data)

        # from_response
        if isinstance(response_body, (dict)):
            response_list = self.config.get("capture.from_response")
            response_data = self.__capture_from_dict(response_list, params, response_body, "response", verbose)
            capture_data.merge_config(response_data)

        # from_config
        config_list = self.config.get("capture.from_config")
        config_data = self.__capture_from_config(config_list, params)
        capture_data.merge_config(config_data)

        # from_header
        config_list = self.config.get("capture.from_header")
        header_data = self.__capture_from_headers(config_list, params, headers, verbose)
        capture_data.merge_config(header_data)

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

    def __render_payload(self, params, data):
        # Check if a user-provided payload is required
        if self.config.get("required_payload") and data is None:
            print("A data payload must be provided for this request")
            exit(1)

        # Render the payload if it hasn't been already
        if self.payload is None:
            template = data or self.config.get("payload")
            self.payload = render_template(template, params.get(""))
        return self.payload

    def __get_response_type(self):
        # Check to see if there is a forced response type
        response_type = self.config.get("response_type")
        if response_type is None:
            return None

        try:
            return ResponseType[response_type.upper()]
        except:
            print("Unrecognized response type '%s'" % response_type)
            exit(1)

    def __capture_from_dict(self, capture_list, params, dict, source, verbose):
        capture_data = YamlConfig()
        if capture_list is None:
            return capture_data

        for capture in capture_list:
            path = render_template(capture["path"], params.get(""))
            dest = render_template(capture["dest"], params.get(""))

            value = self.__parse_dict(dict, path)
            if value is None:
                if verbose:
                    print("Unable to extract value '%s' from %s" % (path, source))
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

    def __capture_from_headers(self, capture_list, params, headers, verbose):
        capture_data = YamlConfig()
        if capture_list is None:
            return capture_data

        for capture in capture_list:
            name = render_template(capture["name"], params.get(""))
            dest = render_template(capture["dest"], params.get(""))

            if name not in headers:
                if verbose:
                    print("Header '%s' not found" % name)
            else:
                value = headers[name]
                capture_data.set(dest, value)

        return capture_data

    def __load_payload(self, value):
        try:
            return json.loads(value)
        except ValueError:
            try:
                # Try parsing as xml if json fails
                return xmltodict.parse(value)
            except ExpatError:
                return {}

    def __parse_dict(self, dict, path):
        scope = dict
        for key in path.split("."):
            if key == "":
                continue
            elif key in scope:
                scope = scope[key]
            else:
                return None
        return scope
