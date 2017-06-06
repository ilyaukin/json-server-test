import requests

from clients.infra import JSON_SERVER_URL

URL = '%s/users' % JSON_SERVER_URL

def post(json):
    requests.post(URL, json=json)

def get(**kwargs):
    response = requests.get(URL, params=kwargs)
    return response.json()