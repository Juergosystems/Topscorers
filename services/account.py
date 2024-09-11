import os
import sys
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from utils.logger import logger
from config import Config as cfg
import requests
import json

class Account:

    def __init__(self):
        try:
            with open(os.path.join(parent_dir, 'topscorer_credentials.json'), 'r') as file:
                credentials = json.load(file)

            url = 'https://topscorers.ch/api/login'
            self.header = cfg.ts.BASIC_HEADERS
            self.jwt_token = requests.post(url, json=credentials, headers=self.header).text
            self.header["Authorization"] = f'Bearer {self.jwt_token}'
        
        except Exception as e:
            logger.error(f'Ein Fehler ist aufgetreten: {e}')

    def get_account_details(self):
        try:
            url = 'https://topscorers.ch/api/user/teams'
            request_response = requests.get(url, headers=self.header).json()
            print(request_response)
            return request_response

        except Exception as e:
            logger.error(f'Ein Fehler ist aufgetreten: {e}')

    def get_login_bonus(self):
        try:
            url = 'https://topscorers.ch/api/user/teams'
            request_response = requests.get(url, headers=self.header).json()
            if request_response["bonus"] is not None:
                logger.info(f'Bonus erfolgreich erhalten.')
                print("Bonus erfolgreich erhalten.")
                return "Bonus erfolgreich erhalten."
            else:
                logger.info(f'Bonus bereits erhalten.')
                print("Bonus bereits erhalten.")
                return "Bonus bereits erhalten."

        except Exception as e:
            logger.error(f'Ein Fehler ist aufgetreten: {e}')

    def get_manager_ranking(self):
        try:
            url = f'https://topscorers.ch/api/user/leagues/{cfg.ts.LEAGUE_ID}/ranking'
            request_response = requests.get(url, headers=self.header).json()["regular_season"]
            print(request_response)
            return request_response

        except Exception as e:
            logger.error(f'Ein Fehler ist aufgetreten: {e}')   

    def get_roster(self):
        try:
            url = f'https://topscorers.ch/api/user/teams/{cfg.ts.TEAM_ID}'
            request_response = requests.get(url, headers=self.header).json()["data"]["players"]
            print(request_response)
            return request_response

        except Exception as e:
            logger.error(f'Ein Fehler ist aufgetreten: {e}')

    def get_lineup(self):
        try:
            url = f'https://topscorers.ch/api/user/teams/{cfg.ts.TEAM_ID}'
            request_response = requests.get(url, headers=self.header).json()["data"]["lineup"]
            print(request_response)
            return request_response

        except Exception as e:
            logger.error(f'Ein Fehler ist aufgetreten: {e}')

    def get_teams_ranking(self):
        try:
            url = f'https://topscorers.ch/api/rankings'
            request_response = requests.get(url, headers=self.header).json()
            print(request_response)
            return request_response

        except Exception as e:
            logger.error(f'Ein Fehler ist aufgetreten: {e}')   

    def get_game_schedule(self):
        try:
            url = f'https://topscorers.ch/api/games'
            request_response = requests.get(url, headers=self.header).json()
            print(request_response)
            return request_response
 
        except Exception as e:
            logger.error(f'Ein Fehler ist aufgetreten: {e}')

    def get_next_round_and_live_details(self):
        try:
            url = f'https://topscorers.ch/api/live?user_team={cfg.ts.TEAM_ID}&all=1'
            request_response = requests.get(url, headers=self.header).json()
            print(request_response)
            return request_response
 
        except Exception as e:
            logger.error(f'Ein Fehler ist aufgetreten: {e}')

    def get_transfermarket_status(self):
        try:
            url = f'https://topscorers.ch/api/user/leagues/{cfg.ts.LEAGUE_ID}/transfers'
            request_response = requests.get(url, headers=self.header).json()["meta"]
            print(request_response)
            return request_response

        except Exception as e:
            logger.error(f'Ein Fehler ist aufgetreten: {e}')

    def get_transfermarket_offers(self, mode):
        try:
            url = f'https://topscorers.ch/api/user/leagues/{cfg.ts.LEAGUE_ID}/transfers'
            request_response = requests.get(url, headers=self.header).json()["data"]
            if mode == "buying":
                request_response = [item for item in request_response if item["user_id"] != cfg.ts.USER_ID]
            elif mode == "selling":
                request_response = [item for item in request_response if item["user_id"] == cfg.ts.USER_ID]
            print(request_response)
            return request_response

        except Exception as e:
            logger.error(f'Ein Fehler ist aufgetreten: {e}')

    def get_player_detail(self, player_id):
        try:
            url = f'https://topscorers.ch/api/players/{player_id}'
            request_response = requests.get(url, headers=self.header).json()
            print(request_response)
            return request_response

        except Exception as e:
            logger.error(f'Ein Fehler ist aufgetreten: {e}')

    def get_league_ticker(self):
        try:
            url = f'https://topscorers.ch/api/user/leagues/{cfg.ts.LEAGUE_ID}/ticker'
            request_response = requests.get(url, headers=self.header).json()["data"]
            
            modified_data = []
            for obj in request_response:
                new_obj = {
                    "created_at": obj['created_at'],
                    "user_name": obj['content'][0]['text'], 
                    "content": ' '.join([item['text'] for item in obj['content']])
                }
                
                modified_data.append(new_obj)

            print(modified_data)
            return modified_data

        except Exception as e:
            logger.error(f'Ein Fehler ist aufgetreten: {e}') 

    def place_bid(self, offer_id, price):
        try:
            url = f'https://topscorers.ch/api/user/transfers/{offer_id}/offers'
            body = json.dumps({"price": str(price)})
            request_response = requests.post(url, headers=self.header, data=body)
            print(request_response.status_code, request_response.text)
            return request_response.text

        except Exception as e:
            logger.error(f'Ein Fehler ist aufgetreten: {e}')

    def update_bid(self, offer_id, bid_id, price):
        try:
            url = f'https://topscorers.ch/api/user/transfers/{offer_id}/offers/{bid_id}'
            body = json.dumps({"price": str(price)})
            request_response = requests.put(url=url, headers=self.header, data=body)
            print(request_response.status_code, request_response.text)
            return request_response.text

        except Exception as e:
            logger.error(f'Ein Fehler ist aufgetreten: {e}')

    def delete_bid(self, offer_id, bid_id):
        try:
            url = f'https://topscorers.ch/api/user/transfers/{offer_id}/offers/{bid_id}'
            request_response = requests.delete(url=url, headers=self.header)
            print(request_response.status_code, request_response.text)
            return request_response.text

        except Exception as e:
            logger.error(f'Ein Fehler ist aufgetreten: {e}')

    def place_offer(self, player_id, price):
        try:
            url = f'https://topscorers.ch/api/user/leagues/{cfg.ts.LEAGUE_ID}/transfers'
            body = json.dumps({"player_id": player_id, "price": str(price)})
            request_response = requests.post(url=url, headers=self.header, data=body)
            print(request_response.status_code, request_response.text)
            return request_response.text

        except Exception as e:
            logger.error(f'Ein Fehler ist aufgetreten: {e}')

    def update_offer(self, offer_id, price):
        try:
            url = f'https://topscorers.ch/api/user/transfers/{offer_id}'
            body = json.dumps({"price": str(price)})
            request_response = requests.put(url=url, headers=self.header, data=body)
            print(request_response.status_code, request_response.text)
            return request_response.text

        except Exception as e:
            logger.error(f'Ein Fehler ist aufgetreten: {e}')

    def delete_offer(self, offer_id):
        try:
            url = f'https://topscorers.ch/api/user/transfers/{offer_id}'
            request_response = requests.delete(url=url, headers=self.header)
            print(request_response.status_code, request_response.text)
            return request_response.text

        except Exception as e:
            logger.error(f'Ein Fehler ist aufgetreten: {e}')
    
    def accept_bid(self, offer_id, bid_id, price):
        try:
            url = f'https://topscorers.ch/api/user/transfers/{offer_id}/offers/{bid_id}/accept'
            body = json.dumps({"price": price})
            request_response = requests.post(url=url, headers=self.header, data=body)
            print(request_response.status_code, request_response.text)
            return request_response.text

        except Exception as e:
            logger.error(f'Ein Fehler ist aufgetreten: {e}')
        

if __name__ == '__main__':

    acc = Account()

    # acc.get_account_details()
    # acc.get_login_bonus()
    # acc.get_manager_ranking()
    # acc.get_roster()
    # acc.get_lineup()
    # acc.get_teams_ranking()
    # acc.get_game_schedule()
    # acc.get_next_round_and_live_details()
    # acc.get_transfermarket_status()
    # acc.get_transfermarket_offers("buying")
    # acc.get_transfermarket_offers("selling")
    acc.get_player_detail(317063)
    # acc.get_league_ticker()
    # acc.place_bid(98624347, 126735)
    # acc.update_bid(98624347,8360345, 127633)
    # acc.delete_bid(98624347,8360345)
    # acc.place_offer(310640, 900000)
    # acc.update_offer(98915611, 115000)
    # acc.delete_offer(98967235)
    # acc.accept_bid(99136049, 8396053, 350200)

