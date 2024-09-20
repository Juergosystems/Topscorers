import os
import sys
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from utils.logger import logger
from config import Config as cfg
import requests
import json
from datetime import datetime as dt, timedelta
import copy

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
            url = 'https://topscorers.ch/api/user/teams?team={cfg.ts.TEAM_ID}'
            request_response = requests.get(url, headers=self.header).json()
            return request_response

        except Exception as e:
            logger.error(f'Ein Fehler ist aufgetreten: {e}')

    def get_login_bonus(self):
        try:
            url = 'https://topscorers.ch/api/user/teams'
            request_response = requests.get(url, headers=self.header).json()
            last_bonus_date = {"last_bonus": dt.now().strftime("%d.%m.%Y")}
            with open (os.path.join(parent_dir, 'assets/last_bonus.json'), "w") as json_file:
                json.dump(last_bonus_date, json_file, indent=4)
            self.last_login_bonus = dt.now().date()
            if request_response["bonus"] is not None:
                logger.info(f'Bonus erfolgreich erhalten.')
                return "Bonus erfolgreich erhalten."
            else:
                logger.info(f'Bonus bereits erhalten.')
                return "Bonus bereits erhalten."

        except Exception as e:
            logger.error(f'Ein Fehler ist aufgetreten: {e}')

    def get_last_bonus_date(self):
        try:
            with open (os.path.join(parent_dir, 'assets/last_bonus.json'), "r") as json_file:
                last_bonus = dt.strptime(json.load(json_file)["last_bonus"], ("%d.%m.%Y"))
        except FileNotFoundError:
            last_bonus = dt.now()-timedelta(days=1)
            last_bonus_date = {"last_bonus": last_bonus.strftime("%d.%m.%Y")}
            with open (os.path.join(parent_dir, 'assets/last_bonus.json'), "w") as json_file:
                json.dump(last_bonus_date, json_file, indent=4)

        return last_bonus

    def get_manager_ranking(self):
        try:
            url = f'https://topscorers.ch/api/user/leagues/{cfg.ts.LEAGUE_ID}/ranking'
            request_response = requests.get(url, headers=self.header).json()["data"]
            return request_response

        except Exception as e:
            logger.error(f'Ein Fehler ist aufgetreten: {e}')   

    def get_roster(self, mode=None):
        try:
            url = f'https://topscorers.ch/api/user/teams/{cfg.ts.TEAM_ID}'
            request_response = requests.get(url, headers=self.header).json()["data"]["players"]
            if mode == "player_ids":
                request_response = [player['id'] for player in request_response]
        
            return request_response

        except Exception as e:
            logger.error(f'Ein Fehler ist aufgetreten: {e}')

    def get_lineup_details(self):
        try:
            url = f'https://topscorers.ch/api/user/teams/{cfg.ts.TEAM_ID}'
            request_response = requests.get(url, headers=self.header).json()["data"]["lineup"]
            return request_response

        except Exception as e:
            logger.error(f'Ein Fehler ist aufgetreten: {e}')
        
    def get_current_lineup(self):
        try:
            url = f'https://topscorers.ch/api/user/teams/{cfg.ts.TEAM_ID}'
            request_response = requests.get(url, headers=self.header).json()["data"]["lineup"]
            current_lineup_ids = {
                "players": {str(item['position_id']): item['current'] for item in request_response}
                    }
            
            current_lineup_names = copy.deepcopy(current_lineup_ids)
            id_to_name = {player["id"]: f'{player["firstname"]} {player["lastname"]}' for player in self.get_roster()}
            for key, player_id in current_lineup_names["players"].items():
                if player_id in id_to_name:
                    current_lineup_names["players"][key] = id_to_name[player_id]

            return (current_lineup_ids, current_lineup_names)

        except Exception as e:
            logger.error(f'Ein Fehler ist aufgetreten: {e}') 

    def update_lineup(self, new_lineup):
        try:
            url = f'https://topscorers.ch/api/user/teams/{cfg.ts.TEAM_ID}/lineup'
            body = json.dumps(new_lineup)
            request_response = requests.post(url=url, headers=self.header, data=body)
            logger.info(request_response.json()["meta"]["status"])
            return json.dumps(request_response.json()["meta"]["status"])

        except Exception as e:
            logger.error(f'Ein Fehler ist aufgetreten: {e}') 

    def get_teams_ranking(self):
        try:
            url = f'https://topscorers.ch/api/rankings'
            request_response = requests.get(url, headers=self.header).json()
            return request_response

        except Exception as e:
            logger.error(f'Ein Fehler ist aufgetreten: {e}')   

    def get_game_schedule(self):
        try:
            url = f'https://topscorers.ch/api/games'
            request_response = requests.get(url, headers=self.header).json()
            return request_response
 
        except Exception as e:
            logger.error(f'Ein Fehler ist aufgetreten: {e}')

    def get_next_round(self, mode="date"):
        try:
            url = f'https://topscorers.ch/api/live?user_team={cfg.ts.TEAM_ID}&all=1'
            request_response = requests.get(url, headers=self.header).json()
            next_round = (dt.strptime(str(request_response["next_live_date"]), "%Y-%m-%dT%H:%M:%S.%fZ") + timedelta(hours=2))
            count_down = request_response["next_live_in_seconds"]
            
            if mode == "countdown":
                return count_down
            else:
                return next_round
 
        except Exception as e:
            logger.error(f'Ein Fehler ist aufgetreten: {e}')

    def get_live_lineup(self):
        try:
            url = f'https://topscorers.ch/api/live?user_team={cfg.ts.TEAM_ID}&all=1'
            request_response = requests.get(url, headers=self.header).json()
            return request_response
 
        except Exception as e:
            logger.error(f'Ein Fehler ist aufgetreten: {e}')

    def get_live_results(self):
        try:
            url = f'https://topscorers.ch/api/live?user_team={cfg.ts.TEAM_ID}&all=1'
            request_response = requests.get(url, headers=self.header).json()["games"]
            return request_response
 
        except Exception as e:
            logger.error(f'Ein Fehler ist aufgetreten: {e}')

    def get_transfermarket_status(self):
        try:
            url = f'https://topscorers.ch/api/user/leagues/{cfg.ts.LEAGUE_ID}/transfers'
            request_response = requests.get(url, headers=self.header).json()["meta"]
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
            return request_response

        except Exception as e:
            logger.error(f'Ein Fehler ist aufgetreten: {e}')

    def get_player_detail(self, player_id):
        try:
            url = f'https://topscorers.ch/api/players/{player_id}'
            request_response = requests.get(url, headers=self.header).json()
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

            return modified_data

        except Exception as e:
            logger.error(f'Ein Fehler ist aufgetreten: {e}') 

    def place_bid(self, offer_id, price):
        try:
            url = f'https://topscorers.ch/api/user/transfers/{offer_id}/offers'
            body = json.dumps({"price": str(price)})
            request_response = requests.post(url, headers=self.header, data=body)
            return request_response.text

        except Exception as e:
            logger.error(f'Ein Fehler ist aufgetreten: {e}')

    def update_bid(self, offer_id, bid_id, price):
        try:
            url = f'https://topscorers.ch/api/user/transfers/{offer_id}/offers/{bid_id}'
            body = json.dumps({"price": str(price)})
            request_response = requests.put(url=url, headers=self.header, data=body)
            return request_response.text

        except Exception as e:
            logger.error(f'Ein Fehler ist aufgetreten: {e}')

    def delete_bid(self, offer_id, bid_id):
        try:
            url = f'https://topscorers.ch/api/user/transfers/{offer_id}/offers/{bid_id}'
            request_response = requests.delete(url=url, headers=self.header)
            return request_response.text

        except Exception as e:
            logger.error(f'Ein Fehler ist aufgetreten: {e}')

    def place_offer(self, player_id, price):
        try:
            url = f'https://topscorers.ch/api/user/leagues/{cfg.ts.LEAGUE_ID}/transfers'
            body = json.dumps({"player_id": player_id, "price": str(price)})
            request_response = requests.post(url=url, headers=self.header, data=body)
            return request_response.text

        except Exception as e:
            logger.error(f'Ein Fehler ist aufgetreten: {e}')

    def update_offer(self, offer_id, price):
        try:
            url = f'https://topscorers.ch/api/user/transfers/{offer_id}'
            body = json.dumps({"price": str(price)})
            request_response = requests.put(url=url, headers=self.header, data=body)
            return request_response.text

        except Exception as e:
            logger.error(f'Ein Fehler ist aufgetreten: {e}')

    def delete_offer(self, offer_id):
        try:
            url = f'https://topscorers.ch/api/user/transfers/{offer_id}'
            request_response = requests.delete(url=url, headers=self.header)
            return request_response.text

        except Exception as e:
            logger.error(f'Ein Fehler ist aufgetreten: {e}')
    
    def accept_bid(self, offer_id, bid_id, price):
        try:
            url = f'https://topscorers.ch/api/user/transfers/{offer_id}/offers/{bid_id}/accept'
            body = json.dumps({"price": price})
            request_response = requests.post(url=url, headers=self.header, data=body)
            return request_response.text

        except Exception as e:
            logger.error(f'Ein Fehler ist aufgetreten: {e}')
        

if __name__ == '__main__':

    acc = Account()

    # print(acc.get_account_details())
    # print(acc.get_login_bonus())
    # print(acc.get_last_bonus_date())
    # print(acc.get_manager_ranking())   
    # print(acc.get_roster())
    # print(acc.get_roster(mode="player_ids"))
    # print(acc.get_lineup_details())
    # print(acc.get_current_lineup())
    # print(acc.update_lineup(acc.get_current_lineup()))
    # print(acc.get_teams_ranking())
    # print(acc.get_game_schedule())
    # print(acc.get_next_round(mode="date"))
    # print(acc.get_next_round(mode="countdown"))
    print(acc.get_live_lineup())
    # print(acc.get_live_results())
    # print(acc.get_transfermarket_status())
    # print(acc.get_transfermarket_offers("buying"))
    # print(acc.get_transfermarket_offers("selling"))
    # print(acc.get_player_detail(317063))
    # print(acc.get_league_ticker())
    # print(acc.place_bid(98624347, 126735))
    # print(acc.update_bid(98624347,8360345, 127633))
    # print(acc.delete_bid(98624347,8360345))
    # print(acc.place_offer(310640, 900000))
    # print(acc.update_offer(98915611, 115000))
    # print(acc.delete_offer(98967235))
    # print(acc.accept_bid(99136049, 8396053, 350200))

