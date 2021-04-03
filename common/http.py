import requests


class Http(object):

    def Get(self):
        pass

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
