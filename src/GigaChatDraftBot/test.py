import requests
import uuid
import logging
from config import AUTH_KEY


def get_gigachat_token(auth_token, scope='GIGACHAT_API_PERS'):
    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
        'RqUID': str(uuid.uuid4()),
        'Authorization': f'Basic {auth_token}'
    }
    payload = {'scope': scope}
    logging.captureWarnings(True)
    response = requests.post(url, headers=headers, data=payload, verify=False)
    response.raise_for_status()
    return response.json()['access_token']


#ключ авторизации из личного кабинета
auth_key = AUTH_KEY
token = get_gigachat_token(auth_key)

def response_gigachat(promt, token=token):
    url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }

    payload = {
        "model": "GigaChat",
        "messages": [
            {"role": "user", "content": promt}
        ],
        "temperature": 0.7
    }

    response = requests.post(url, headers=headers, json=payload, verify=False)
    answer = response.json()
    return answer['choices'][0]['message']['content']