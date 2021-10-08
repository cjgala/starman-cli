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
