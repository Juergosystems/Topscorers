import os
import sys
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(parent_dir)

from utils.logger import logger
from config import Config as cfg
from datetime import datetime as dt
import requests
import json


def get_jwt_token():
    try:
        # Datei credentials.json einlesen
        with open(os.path.join(parent_dir, 'topscorer_credentials.json'), 'r') as file:
            credentials = json.load(file)

        url = 'https://topscorers.ch/api/login'
        headers = cfg.ts.BASIC_HEADERS
        request_response = requests.post(url, json=credentials, headers=headers).text
        return request_response
    
    except Exception as e:
        logger.error(f'Ein Fehler ist aufgetreten: {e}')

def get_login_bonus(jwt_token):
    try:
        url = 'https://topscorers.ch/api/user/teams'
        headers = cfg.ts.BASIC_HEADERS
        headers["Authorization"] = f'Bearer {jwt_token}'
        request_response = requests.get(url, headers=headers).json()
        if request_response["bonus"] is not None:
            logger.info(f'Bonus erfolgreich erhalten.')
            return "Bonus erfolgreich erhalten."
        else:
            logger.info(f'Bonus bereits erhalten.')
            return "Bonus bereits erhalten."

    except Exception as e:
        logger.error(f'Ein Fehler ist aufgetreten: {e}')

def get_account_overview(jwt_token):
    try:
        url = 'https://topscorers.ch/api/user/teams'
        headers = cfg.ts.BASIC_HEADERS
        headers["Authorization"] = f'Bearer {jwt_token}'
        request_response = requests.get(url, headers=headers).json()
        return request_response

    except Exception as e:
        logger.error(f'Ein Fehler ist aufgetreten: {e}')

def get_team_overview(jwt_token):
    try:
        url = f'https://topscorers.ch/api/user/teams/{cfg.ts.TEAM_ID}'
        headers = cfg.ts.BASIC_HEADERS
        headers["Authorization"] = f'Bearer {jwt_token}'
        request_response = requests.get(url, headers=headers).json()
        return request_response

    except Exception as e:
        logger.error(f'Ein Fehler ist aufgetreten: {e}')

    

if __name__ == '__main__':

    jwt_token = get_jwt_token()
    login_bonus_status = get_login_bonus(jwt_token)
    print(login_bonus_status)
