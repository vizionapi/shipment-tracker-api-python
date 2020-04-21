import requests
import os
import json

VIZION_API_KEY = os.environ['VIZION_API_KEY']
VIZION_API_URL = os.environ['VIZION_API_URL']

def create_subscription(identifier, scac, is_bol = False):
    '''
    Call the Vizion API to create a new reference subscription.\n
    On successful response, returns the reference ID.
    '''
    data = {
        'scac': scac,
        'callback_url': 'http://localhost:5000/webhook'
    }
    if is_bol:
        data['bill_of_lading'] = identifier
    else:
        data['container_id'] = identifier
    try:
        headers = {'X-API-Key': VIZION_API_KEY}
        r = requests.post(f'{VIZION_API_URL}/references', json=data, headers=headers)
        res = r.json()
        return res['reference']['id']
    except requests.exceptions.RequestException as e:
        raise e