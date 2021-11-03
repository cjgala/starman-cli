from config import YamlConfig
from jinja2 import Template, Undefined
from requester import Requester

class SilentUndefined(Undefined):
    def _fail_with_undefined_error(self, *args, **kwargs):
        return ''

class ChartRequest:
    def __init__(self, sourcefile):
        self.config = YamlConfig(sourcefile)

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
        return template.render(params.get(""))

    def __render_headers(self, params):
        headers = self.config.get("headers")
        render = {}
        if headers is None:
            return render

        for key in headers:
            template = Template(headers[key], undefined=SilentUndefined)
            render[key] = template.render(params.get(""))
        return render

    def __render_payload(self, params):
        payload = self.config.get("payload")
        template = Template(payload, undefined=SilentUndefined)
        return template.render(params.get(""))

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
