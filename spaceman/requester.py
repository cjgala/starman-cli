import requests

from http.client import responses
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from spaceman.response import Response

class Requester:
    def __init__(self, host, ssl_verify=False, verbose=False, curl=False, test=False):
        self.host = host
        self.ssl_verify = ssl_verify
        self.verbose = verbose
        self.curl = curl
        self.test = test

        if not self.ssl_verify:
            requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    def get(self, path, headers):
        self.__print_request("GET", path, headers)
        if self.test:
            return None, None, None

        try:
            r = requests.get(self.host + path, headers=headers, verify=self.ssl_verify)
            return Response(r)
        except Exception as ex:
            print(ex)
            exit(2)

    def post(self, path, headers, payload):
        self.__print_request("POST", path, headers, payload)
        if self.test:
            return None, None, None

        try:
            r = requests.post(self.host + path, headers=headers, data=payload, verify=self.ssl_verify)
            return Response(r)
        except Exception as ex:
            print(ex)
            exit(2)

    def put(self, path, headers, payload):
        self.__print_request("PUT", path, headers, payload)
        if self.test:
            return None, None, None

        try:
            r = requests.put(self.host + path, headers=headers, data=payload, verify=self.ssl_verify)
            return Response(r)
        except Exception as ex:
            print(ex)
            exit(2)

    def patch(self, path, headers, payload):
        self.__print_request("PATCH", path, headers, payload)
        if self.test:
            return None, None, None

        try:
            r = requests.patch(self.host + path, headers=headers, data=payload, verify=self.ssl_verify)
            return Response(r)
        except Exception as ex:
            print(ex)
            exit(2)

    def delete(self, path, headers):
        self.__print_request("DELETE", path, headers)
        if self.test:
            return None, None, None

        try:
            r = requests.delete(self.host + path, headers=headers, verify=self.ssl_verify)
            return Response(r)
        except Exception as ex:
            print(ex)
            exit(2)

    def __print_request(self, action, path, headers, payload=None):
        if self.curl:
            lines = []

            secure = " "
            if not self.ssl_verify:
                secure = " -k "
            lines.append("curl -X %s%s%s" % (action, secure, self.host+path))
            for key, value in headers.items():
                lines.append("-H '%s: %s'" % (key, value))
            if payload:
                lines.append("-d '%s'" % payload)

            print(" \\\n".join(lines).replace("\n", "\n     ") + "\n")

        elif self.verbose:
            print("%s %s" % (action, path))
            if payload:
                print(payload)
            print("")