import requests


class Http(object):

    @staticmethod
    def Get(url, headers=None):
        if not headers:
            headers = {"content-type": "application/json"}
        req = requests.get(url, headers=headers)
        if req.status_code == 200:
            try:
                return req.json(), True
            except:
                return req.text, False
        else:
            return req.json(), True

    @staticmethod
    def Post(url, data, headers=None):
        if not headers:
            headers = {"content-type": "application/json"}
        req = requests.post(url, json=data, headers=headers)
        if req.status_code == 200:
            try:
                return req.json(), True
            except:
                return req.text, False
        else:
            return req.json(), True

    @staticmethod
    def Put():
        pass

    def Delete(self):
        pass
