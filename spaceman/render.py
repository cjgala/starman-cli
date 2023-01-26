import base64
import uuid

from jinja2 import Template, Undefined

def render_template(text, params):
   if text is None:
     return None

   template = Template(text, undefined=SilentUndefined)
   template.globals["increment"] = lambda x: int(x) + 1
   template.globals["random_uuid"] = lambda: uuid.uuid4()
   template.globals["basic_auth"] = basic_auth
   return template.render(params)

def basic_auth(username, password):
  data = bytes(username + ":" + password, "utf-8")
  return "Basic " + base64.b64encode(data).decode("utf-8")

class SilentUndefined(Undefined):
    def _fail_with_undefined_error(self, *args, **kwargs):
        return ''
