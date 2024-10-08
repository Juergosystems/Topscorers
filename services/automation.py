import os
import sys
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from utils.logger import logger
from utils import telegram_helper
from services import account, monitoring, intelligence
from config import Config as cfg
from datetime import datetime as dt
import json

tlgm = telegram_helper.TelegramHelper()
acc = account.Account()
mnt = monitoring.Monitor()
intl = intelligence.Intelligence()


class Automation:
    
    def __init__(self):

        self.next_round = acc.get_next_round(mode="date")
        self.count_down = acc.get_next_round(mode="countdown")
    
    def bonus_handler(self, mode="info"):

        if acc.get_last_bonus_date().date() < dt.now().date():

            if mode == "automated":
                    if acc.get_login_bonus() == 'Bonus erfolgreich erhalten.':
                        topic = "Login Bonus Received!"
                        body = f'You have received the login bonus for today {dt.now().strftime("%d.%m.%Y")}.'
                        tlgm.send_message(topic, body)

            else:
                    topic = "Login Bonus Reminder!"
                    body = f'Do not forget login to receive your daily bonus.'
                    tlgm.send_message(topic, body)

    
    def balance_handler(self, mode="info"):
        
        if (mnt.negative_balance() and self.count_down <= cfg.atm.ALERT_OFFSET):
            if mode == "automated":
                print("No automated handling implemented yet.")
            else:
                topic = "Negative Balance!"
                body = f'Your account balance is negative. Please sell a player to be ready for the next round starting {self.next_round.strftime("%d.%m.%Y")} {self.next_round.strftime("%H:%M")}.'
                tlgm.send_message(topic, body)
        else:
            return


    def lineup_handler(self, mode="info"):
        
        current_lineup = acc.get_current_lineup()
        recommended_lineup = intl.get_line_up_reccomendation()

        players_out = {}
        players_in = {}

        for key, value in current_lineup[1]["players"].items():
            if value not in recommended_lineup[1]["players"].values():
                players_out[key] = value

        for key, value in recommended_lineup[1]["players"].items():
            if value not in current_lineup[1]["players"].values():
                players_in[key] = value

        if not players_out and not players_in:
            return

        if (mnt.missing_player_in_the_lineup() or self.count_down <= cfg.atm.NEXT_ROUND_ALERT_OFFSET):            
            if mode == "automated":
                acc.update_lineup(recommended_lineup[0])
                topic = "Lineup Updated!"
                body = "Players out: \n" + "\n".join([f" •  {players_out[key]}" for key in players_out]) + "\n\nPlayers in: \n" + "\n".join([f" •  {players_in[key]}" for key in players_in])
                tlgm.send_message(topic, body)

            else:
                topic = "Lineup Recommendation"
                body = "Players out: \n" + "\n".join([f" •  {players_out[key]}" for key in players_out]) + "\n\nPlayers in: \n" + "\n".join([f" •  {players_in[key]}" for key in players_in])
                tlgm.send_message(topic, body)

        else:
            return
        

    def transfermarket_handler(self, mode="info"):

        try:
            with open(os.path.join(parent_dir, 'assets/player_of_interest.json'), 'r') as json_file:
                players_of_interest = json.load(json_file)
        except FileNotFoundError:
            players_of_interest = []

        if (mnt.transfermarket_update()):
            score_table = intl.get_player_scores(mnt.new_player_ids, mode="efficiency")

            for player in score_table:
                players_of_interest.append(player)
        
        current_offers = acc.get_transfermarket_offers("buying")

        for player in players_of_interest:
                for offer in current_offers:
                    if player["id"] == offer["player"]["id"]:
                        player["offer_id"] = offer["id"]
                        player["expires_in"] = offer["expires_in"]
                        player["marketValue"] = offer["player"]["marketvalue"]
                        player["marketValueTrend"] = offer["player"]["marketvalue_trend"]
                        break
        
        new_players_of_interest = [player for player in players_of_interest if ((player["expires_in"]) and (player['score'] > cfg.atm.TRANSFERMARKET_ALERT_SCORE or player["marketValueTrend"] in cfg.atm.TRANSFERMAKRET_ALERT_TREND or player["team"] in cfg.atm.TRANSFERMAKRET_ALERT_FAVORITE_TEAMS))]
        alerting_players = [player for player in new_players_of_interest if (player["expires_in"] <= cfg.atm.TRANSFERMARKET_ALERT_OFFSET)]

        if not alerting_players:
            return
        
        updated_player_of_interests = [player for player in new_players_of_interest if player not in alerting_players]

        with open(os.path.join(parent_dir, 'assets/player_of_interest.json'), "w") as json_file:
            json.dump(updated_player_of_interests, json_file, indent=4)

        if mode == "automated":
            print("No automated handling implemented yet.")
        else:
            for player in alerting_players:
                tlgm.send_biding_request(player)
                
        return



    
if __name__ == '__main__':

    atm = Automation()
    
    # atm.bonus_handler(mode="info")
    # atm.bonus_handler(mode="automated")

    # atm.balance_handler(mode="info")
    # atm.balance_handler(mode="automated")

    # atm.lineup_handler(mode="info")
    # atm.lineup_handler(mode="automated")

    atm.transfermarket_handler(mode="info")
    

    
