import json
import requests

class Requester:
    def __init__(self, host, verbose=False, test=False):
        self.host = host
        self.verbose = verbose
        self.test = test

    def get(self, path, headers):
        if self.verbose:
            print("GET %s\n" % path)
        if self.test:
            return None

        try:
            r = requests.get(self.host + path, headers=headers)
            self.__check_response(r)
            return r.json()
        except Exception as ex:
            print(ex)
            exit(2)

    def post(self, path, headers, payload):
        if self.verbose:
            print("POST %s" % path)
            print(payload)
            print("")
        if self.test:
            return None

        try:
            r = requests.post(self.host + path, headers=headers, data=payload)
            self.__check_response(r)
            return r.json()
        except Exception as ex:
            print(ex)
            exit(2)

    def delete(self, path, headers):
        if self.verbose:
            print("DELETE %s\n" % path)
        if self.test:
            return None

        try:
            r = requests.delete(self.host + path, headers=headers)
            return None
        except Exception as ex:
            print(ex)
            exit(2)

    def __print_json(self, data):
        print(json.dumps(data, indent=2))

    def __check_response(self, response):
        if response.status_code > 299:
            try:
                self.__print_json(response.json())
            except Exception:
                print(response.text)
            exit(3)
