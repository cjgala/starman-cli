import os
import uuid
import yaml

from config import YamlConfig
from os.path import isfile, isdir
from jinja2 import Template, Undefined
from requester import Requester

MANIFEST = "manifest.yaml"

def is_chart(dir_path, chart_name):
    manifest_path = dir_path + "/" + chart_name + "/" + MANIFEST
    return isfile(manifest_path)

class SpaceChart:
    def __init__(self, dir_path, chart_name):
        self.name = chart_name
        self.path = dir_path + "/" + chart_name

        manifest_path = self.path + "/" + MANIFEST
        if not isfile(manifest_path):
            print("Unable to load chart '%s'" % chart_name)
            exit(1)
        self.manifest = YamlConfig(manifest_path)

    def print_info(self, print_yaml):
        if print_yaml:
            print("name: %s" % self.name)
            print(yaml.dump(self.manifest.data))
        else:
            print(self.name.upper())
            print("=============================")
            print(self.manifest.get("description"))
            print("\nAVAILBLE REQUESTS:")
            print("- " + "\n- ".join(self.__find_requests(self.path)))
            print("")

    def get_host(self):
        return self.manifest.get("host")

    def get_config(self):
        return self.manifest.get("config")

    def get_request(self, command):
        request_path = self.path + "/" + "/".join(command) + ".yaml"
        if not isfile(request_path):
            print("Unknown command: " + " ".join(command))
            exit(1)
        return ChartRequest(" ".join(command), request_path)

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
    def __init__(self, name, sourcefile):
        self.name = name
        self.config = YamlConfig(sourcefile)

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
            print("")

    def execute(self, host, params, verbose, test):
        self.__validate_params(params)

        client = Requester(host, verbose or test, test)
        endpoint = self.__render_endpoint(params)
        headers = self.__render_headers(params)

        method = self.config.get("method")
        if method == "GET":
            return client.get(endpoint, headers)
        elif method == "POST":
            payload = self.__render_payload(params)
            return client.post(endpoint, headers, payload)
        elif method == "DELETE":
            return client.delete(endpoint, headers)
        else:
            print("Unrecognized method: " + method)
            exit(1)

    def extract_captured_values(self, response):
        capture_data = YamlConfig()
        capture_list = self.config.get("capture")

        if capture_list is None:
            return capture_data

        for capture in capture_list:
            path = capture["value"]
            value = self.__parse_response(response, path)
            if value is None:
                print("WARNING: Unable to extract value '%s' from the response" % path)
            else:
                capture_data.set(capture["dest"], value)

        return capture_data

    def get_cleanup_values(self):
        return self.config.get("cleanup")

    def __validate_params(self, params):
        required_list = self.config.get("required")
        if required_list is None:
            return

        for required in required_list:
            if params.get(required["key"]) is None:
                print(required["message"])
                exit(1)

    def __render_endpoint(self, params):
        endpoint = self.config.get("endpoint")

        template = Template(endpoint, undefined=SilentUndefined)
        self.__add_custom_renders(template)
        return template.render(params.get(""))

    def __render_headers(self, params):
        headers = self.config.get("headers")
        render = {}
        if headers is None:
            return render

        for key in headers:
            template = Template(headers[key], undefined=SilentUndefined)
            self.__add_custom_renders(template)
            render[key] = template.render(params.get(""))
        return render

    def __render_payload(self, params):
        payload = self.config.get("payload")

        template = Template(payload, undefined=SilentUndefined)
        self.__add_custom_renders(template)
        return template.render(params.get(""))

    def __add_custom_renders(self, template):
        template.globals["random_uuid"] = lambda: str(uuid.uuid4())

    def __parse_response(self, response, path):
        scope = response
        for key in path.split("."):
            if key == "":
                continue
            elif key in scope:
                scope = scope[key]
            else:
                return None
        return scope

class SilentUndefined(Undefined):
    def _fail_with_undefined_error(self, *args, **kwargs):
        return ''
