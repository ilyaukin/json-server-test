import requests

from clients.infra import JSON_SERVER_URL

URL = '%s/users' % JSON_SERVER_URL

def post(json):
    requests.post(URL, json=json)

def get(**kwargs):
    response = requests.get(URL, params=kwargs)
    return response.json()

def put(user_id, json):
    requests.put('%s/%s' % (URL, user_id), json=json)

def patch(user_id, json):
    requests.patch('%s/%s' % (URL, user_id), json=json)

def delete(user_id):
    requests.delete('%s/%s' % (URL, user_id))
