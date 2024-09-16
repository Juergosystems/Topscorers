import os
import sys
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from utils.logger import logger
from config import Config as cfg
import requests
import json
from datetime import datetime as dt, timedelta

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
            url = 'https://topscorers.ch/api/user'
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
                last_bonus = {"last_bonus": dt.now().strftime("%d.%m.%Y")}
                with open("../assets/last_bonus.json", 'w') as json_file:
                    json.dump(last_bonus, json_file, indent=4)
                self.last_login_bonus = dt.now().date()
                logger.info(f'Bonus erfolgreich erhalten.')
                print("Bonus erfolgreich erhalten.")
                return "Bonus erfolgreich erhalten."
            else:
                logger.info(f'Bonus bereits erhalten.')
                print("Bonus bereits erhalten.")
                return "Bonus bereits erhalten."

        except Exception as e:
            logger.error(f'Ein Fehler ist aufgetreten: {e}')

    def get_last_bonus_date(self):
        with open ("../assets/last_bonus.json", "r") as json_file:
            last_bonus_date = dt.strptime(json.load(json_file)["last_bonus"], ("%d.%m.%Y") )
            print(last_bonus_date)
            return last_bonus_date

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

    def get_lineup_details(self):
        try:
            url = f'https://topscorers.ch/api/user/teams/{cfg.ts.TEAM_ID}'
            request_response = requests.get(url, headers=self.header).json()["data"]["lineup"]
            print(request_response)
            return request_response

        except Exception as e:
            logger.error(f'Ein Fehler ist aufgetreten: {e}')
        
    def get_current_lineup(self):
        try:
            url = f'https://topscorers.ch/api/user/teams/{cfg.ts.TEAM_ID}'
            request_response = requests.get(url, headers=self.header).json()["data"]["lineup"]
            current_lineup = {
                "players": {str(item['position_id']): item['current'] for item in request_response}
                    }
            print(current_lineup)
            return current_lineup

        except Exception as e:
            logger.error(f'Ein Fehler ist aufgetreten: {e}') 

    def update_lineup(self, new_lineup):
        try:
            url = f'https://topscorers.ch/api/user/teams/{cfg.ts.TEAM_ID}/lineup'
            body = json.dumps(new_lineup)
            request_response = requests.post(url=url, headers=self.header, data=body)
            print(request_response.status_code, json.dumps(request_response.json()["meta"]["status"]))
            logger.info(request_response.json()["meta"]["status"])
            return json.dumps(request_response.json()["meta"]["status"])

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

    def get_next_round(self, mode="date"):
        try:
            url = f'https://topscorers.ch/api/live?user_team={cfg.ts.TEAM_ID}&all=1'
            request_response = requests.get(url, headers=self.header).json()
            next_round = (dt.strptime(str(request_response["next_live_date"]), "%Y-%m-%dT%H:%M:%S.%fZ") + timedelta(hours=2))
            count_down = request_response["next_live_in_seconds"]
            print(next_round)
            print(count_down)
            if mode == "countdown":
                return count_down
            else:
                return next_round
 
        except Exception as e:
            logger.error(f'Ein Fehler ist aufgetreten: {e}')

    def get_live_lineup(self):
        try:
            url = f'https://topscorers.ch/api/live?user_team={cfg.ts.TEAM_ID}&all=1'
            request_response = requests.get(url, headers=self.header).json()["players"]
            print(request_response)
            return request_response
 
        except Exception as e:
            logger.error(f'Ein Fehler ist aufgetreten: {e}')

    def get_live_results(self):
        try:
            url = f'https://topscorers.ch/api/live?user_team={cfg.ts.TEAM_ID}&all=1'
            request_response = requests.get(url, headers=self.header).json()["games"]
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
    acc.get_last_bonus_date()
    # acc.get_manager_ranking()
    # acc.get_roster()
    # acc.get_lineup_details()
    # lineup = acc.get_current_lineup()
    # acc.update_lineup(lineup)
    # acc.get_teams_ranking()
    # acc.get_game_schedule()
    # acc.get_next_round(mode="date")
    # acc.get_next_round(mode="countdown")
    # acc.get_live_lineup()
    # acc.get_live_results()
    # acc.get_transfermarket_status()
    # acc.get_transfermarket_offers("buying")
    # acc.get_transfermarket_offers("selling")
    # acc.get_player_detail(317063)
    # acc.get_league_ticker()
    # acc.place_bid(98624347, 126735)
    # acc.update_bid(98624347,8360345, 127633)
    # acc.delete_bid(98624347,8360345)
    # acc.place_offer(310640, 900000)
    # acc.update_offer(98915611, 115000)
    # acc.delete_offer(98967235)
    # acc.accept_bid(99136049, 8396053, 350200)

