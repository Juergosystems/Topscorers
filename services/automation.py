import os
import sys
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from utils.logger import logger
from utils import telegram
from services import account, monitoring
from config import Config as cfg
from datetime import datetime as dt
import json

tlgm = telegram.Telegram()
acc = account.Account()
mnt = monitoring.Monitor()


class Automation:
    
    def __init__(self):
        return
    
    def bonus_handler(self, mode="info"):

        if acc.get_last_bonus_date().date() < dt.now().date():

            if mode == "automated":
                    acc.get_login_bonus()
                    topic = "Login Bonus Received!"
                    body = f'You have received the login bonus for today {dt.now().strftime("%d.%m.%Y")}.'
                    tlgm.send_message(topic, body)

            else:
                    topic = "Login Bonus Reminder!"
                    body = f'Do not forget login to receive your daily bonus.'
                    tlgm.send_message(topic, body)

    
    def balance_handler(self, mode="info"):

        next_round = acc.get_next_round(mode="date")
        count_down = acc.get_next_round(mode="countdown")
        
        if (mnt.negative_balance() and count_down <= cfg.atm.ALERT_OFFSET):
            if mode == "automated":
                print("No automated handling implemented yet.")
            else:
                topic = "Negative Balance!"
                body = f'Your account balance is negative. Please sell a player to be ready for the next round starting {next_round.strftime("%d.%m.%Y")} {next_round.strftime("%H:%M")}.'
                tlgm.send_message(topic, body)
        else:
            return


    def lineup_handler(self, mode="info"):
        
        next_round = acc.get_next_round(mode="date")
        count_down = acc.get_next_round(mode="countdown")

        if (mnt.missing_player_in_the_lineup() and count_down <= cfg.atm.ALERT_OFFSET):            
            if mode == "automated":
                print("No automated handling implemented yet.")
            else:
                topic = "Missing Player!"
                body = f'You are missing at least one player in your lineup for the next round starting {next_round.strftime("%d.%m.%Y")} {next_round.strftime("%H:%M")}.'
                tlgm.send_message(topic, body)

        else:
            return
        

    def transfermarket_handler(self, mode="info"):
        return



    
if __name__ == '__main__':

    atm = Automation()
    
    # atm.bonus_handler(mode="info")
    # atm.bonus_handler(mode="automated")

    # atm.balance_handler(mode="info")
    # atm.balance_handler(mode="automated")

    # atm.lineup_handler(mode="info")
    # atm.lineup_handler(mode="automated")
    

    
