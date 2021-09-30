import json
import requests

class Requester:
    def __init__(self, host, verbose=False):
        self.host = host
        self.verbose = verbose

    def get(self, path, headers=None):
        if self.verbose:
            print("GET %s\n" % path)

        try:
            r = requests.get(self.host + path, headers=headers)
            self.__check_response(r, path)
            return r.json()
        except Exception as ex:
            print(ex)
            exit(2)

    def post(self, path, payload, headers=None):
        if self.verbose:
            print("POST %s" % path)
            self.__print_json(payload)
            print("")

        try:
            r = requests.post(self.host + path, headers=headers, data=json.dumps(payload))
            self.__check_response(r, path)
            return r.json()
        except Exception as ex:
            print(ex)
            exit(2)

    def __print_json(self, data):
            print(json.dumps(data, indent=2))

    def __check_response(self, response, path):
        if response.status_code > 299:
            self.__print_json(response.json())
            exit(3)
