import json
import requests
from http.client import responses

class Requester:
    def __init__(self, host, verbose=False, test=False):
        self.host = host
        self.verbose = verbose
        self.test = test

    def get(self, path, headers):
        if self.verbose:
            print("GET %s\n" % path)
        if self.test:
            return None, None

        try:
            r = requests.get(self.host + path, headers=headers)
            self.__check_response(r)
            return r.json(), r.status_code
        except Exception as ex:
            print(ex)
            exit(2)

    def post(self, path, headers, payload):
        if self.verbose:
            print("POST %s" % path)
            print(payload)
            print("")
        if self.test:
            return None, None

        try:
            r = requests.post(self.host + path, headers=headers, data=payload)
            self.__check_response(r)
            return r.json(), r.status_code
        except Exception as ex:
            print(ex)
            exit(2)

    def delete(self, path, headers):
        if self.verbose:
            print("DELETE %s\n" % path)
        if self.test:
            return None, None

        try:
            r = requests.delete(self.host + path, headers=headers)
            return None, r.status_code
        except Exception as ex:
            print(ex)
            exit(2)

    def __print_json(self, data):
        print(json.dumps(data, indent=2))

    def __check_response(self, response):
        status = response.status_code
        if status > 299:
            try:
                self.__print_json(response.json())
                if self.verbose:
                    print("%d %s" % (status, responses[status]))
            except Exception:
                print(response.text)
                if self.verbose:
                    print("%d" % status)
            exit(3)
