from config import YamlConfig
from jinja2 import Template, Undefined

class ChartRequest:
    def __init__(self, sourcefile):
        self.config = YamlConfig(sourcefile)

    def get_method(self):
        return self.config.get("method")

    def render_endpoint(self, params):
        endpoint = self.config.get("endpoint")
        template = Template(endpoint, undefined=SilentUndefined)
        return template.render(params.get(""))

    def render_headers(self, params):
        headers = self.config.get("headers")
        render = {}
        for key in headers:
            template = Template(headers[key], undefined=SilentUndefined)
            render[key] = template.render(params.get(""))
        return render

    def render_payload(self, params):
        payload = self.config.get("payload")
        template = Template(payload, undefined=SilentUndefined)
        return template.render(params.get(""))


class SilentUndefined(Undefined):
    def _fail_with_undefined_error(self, *args, **kwargs):
        return ''
