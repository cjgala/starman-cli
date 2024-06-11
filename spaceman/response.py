import json
import xmltodict

from enum import Enum
from xml.dom.minidom import parseString as parseXmlString

class ResponseType(Enum):
    JSON = 1
    XML = 2
    TEXT = 3

class Response:
    def __init__(self, response, type):
        self.status = response.status_code
        self.headers = response.headers
        self.type = self.__get_content_type(type)

        if self.type == ResponseType.JSON:
            try:
                self.body = response.json()
            except Exception:
                self.type = ResponseType.TEXT
                self.body = response.text
        else:
            self.body = response.text

    def get_body(self):
        if self.type == ResponseType.JSON or self.type == ResponseType.TEXT:
            return self.body
        else: # self.type == ResponseType.XML
            return xmltodict.parse(self.body)

    def pretty_print(self):
        if self.type == ResponseType.JSON:
            if isinstance(self.body, (list, dict)):
                self.__print_json()
            elif self.body is not None:
                self.__print_text()
        elif self.type == ResponseType.XML:
            self.__print_xml()
        else: # self.type == ResponseType.TEXT
            self.__print_text()

    def __get_content_type(self, override):
        if override is not None:
            return override
        header = self.headers.get("Content-Type")

        if header is None:
            return ResponseType.TEXT
        elif "json" in header:
            return ResponseType.JSON
        elif "xml" in header:
            return ResponseType.XML
        else:
            return ResponseType.TEXT

    def __print_json(self):
        print(json.dumps(self.body, indent=2))

    def __print_xml(self):
        document = parseXmlString(self.body)
        print(document.toprettyxml())

    def __print_text(self):
        print(self.body)