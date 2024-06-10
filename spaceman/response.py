import json

from enum import Enum

class ResponseType(Enum):
    JSON = 1
    XML = 2
    TEXT = 3

class Response:
    def __init__(self, response):
        self.status = response.status_code
        self.headers = response.headers
        try:
            self.body = response.json()
            self.type = ResponseType.JSON
        except Exception:
            self.body = response.text
            self.type = ResponseType.TEXT

    def get_body(self):
        return self.body

    def pretty_print(self):
        if self.type == ResponseType.JSON:
            if isinstance(self.body, (list, dict)):
                print(json.dumps(self.body, indent=2))
            elif self.body is not None:
                print(self.body)
        else: # self.type == ResponseType.TEXT
            print(self.body)