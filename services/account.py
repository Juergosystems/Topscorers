import os
import sys
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from utils.logger import logger
from config import Config as cfg
from datetime import datetime as dt
import requests
import json

class Account:

    def __init__(self):
        try:
            # Datei credentials.json einlesen
            with open(os.path.join(parent_dir, 'topscorer_credentials.json'), 'r') as file:
                credentials = json.load(file)

            url = 'https://topscorers.ch/api/login'
            basic_header = cfg.ts.BASIC_HEADERS
            jwt_token = requests.post(url, json=credentials, headers=basic_header).text
            basic_header["Authorization"] = f'Bearer {jwt_token}'
            self.header = basic_header
        
        except Exception as e:
            logger.error(f'Ein Fehler ist aufgetreten: {e}')

    def get_login_bonus(self):
        try:
            url = 'https://topscorers.ch/api/user/teams'
            request_response = requests.get(url, headers=self.header).json()
            if request_response["bonus"] is not None:
                logger.info(f'Bonus erfolgreich erhalten.')
                return "Bonus erfolgreich erhalten."
            else:
                logger.info(f'Bonus bereits erhalten.')
                return "Bonus bereits erhalten."

        except Exception as e:
            logger.error(f'Ein Fehler ist aufgetreten: {e}')

    def get_account_details(self):
        try:
            url = 'https://topscorers.ch/api/user/teams'
            request_response = requests.get(url, headers=self.header).json()
            return request_response

        except Exception as e:
            logger.error(f'Ein Fehler ist aufgetreten: {e}')

    def get_roster(self):
        try:
            url = f'https://topscorers.ch/api/user/teams/{cfg.ts.TEAM_ID}'
            request_response = requests.get(url, headers=self.header).json()["data"]["players"]
            return request_response

        except Exception as e:
            logger.error(f'Ein Fehler ist aufgetreten: {e}')

    def get_lineup(self):
        try:
            url = f'https://topscorers.ch/api/user/teams/{cfg.ts.TEAM_ID}'
            request_response = requests.get(url, headers=self.header).json()["data"]["lineup"]
            return request_response

        except Exception as e:
            logger.error(f'Ein Fehler ist aufgetreten: {e}')

        

if __name__ == '__main__':

    acc = Account()

    login_bonus_status = acc.get_login_bonus()
    print(login_bonus_status)

    print(acc.get_account_details())
    print(acc.get_roster())
    print(acc.get_lineup())
