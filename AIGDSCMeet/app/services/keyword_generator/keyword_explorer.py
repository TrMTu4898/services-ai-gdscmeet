import requests

class KeywordsExplorer:
    def __init__(self, api_url):
        self.api_url = api_url

    def get_keywords(self, input_mes):
        data = {'text': input_mes}
        res = requests.post(self.api_url, json=data)
        result = res.json()
        return result
