from config import YamlConfig
from jinja2 import Template, Undefined

class SilentUndefined(Undefined):
    def _fail_with_undefined_error(self, *args, **kwargs):
        return ''

class ChartRequest:
    def __init__(self, sourcefile):
        self.config = YamlConfig(sourcefile)

    def get_method(self):
        return self.config.get("method")

    def validate_params(self, params):
        required_list = self.config.get("required")
        if required_list is None:
            return

        for required in required_list:
            if params.get(required["key"]) is None:
                print(required["message"])
                exit(1)

    def render_endpoint(self, params):
        endpoint = self.config.get("endpoint")
        template = Template(endpoint, undefined=SilentUndefined)
        return template.render(params.get(""))

    def render_headers(self, params):
        headers = self.config.get("headers")
        render = {}
        if headers is None:
            return render

        for key in headers:
            template = Template(headers[key], undefined=SilentUndefined)
            render[key] = template.render(params.get(""))
        return render

    def render_payload(self, params):
        payload = self.config.get("payload")
        template = Template(payload, undefined=SilentUndefined)
        return template.render(params.get(""))

    def get_cleanup_values(self):
        return self.config.get("cleanup")

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
