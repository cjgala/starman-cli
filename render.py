import uuid

from jinja2 import Template, Undefined

def render_template(text, params):
   template = Template(text, undefined=SilentUndefined)
   template.globals["random_uuid"] = lambda: str(uuid.uuid4())
   return template.render(params)

class SilentUndefined(Undefined):
    def _fail_with_undefined_error(self, *args, **kwargs):
        return ''
