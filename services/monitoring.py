import os
import sys
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from utils.logger import logger
from utils import telegram_helper
from services import account
from config import Config
import json


tlgm = telegram_helper.TelegramHelper()
acc = account.Account()

class Monitor:
    
    def __init__(self):
        self.balance = None
        self.empty_lineup_position_ids = None
        self.positions_ids_with_alternatives = None
        self.new_transfermarket_offer_ids = None
        self.new_player_ids = None

        return
    
    def negative_balance(self):
        negative_balance = False
        self.balance = acc.get_account_details()["data"][0]["budget"]
        if   self.balance < 0:
            negative_balance = True
        return negative_balance

    def missing_player_in_the_lineup(self):
        missing_player = False
        lineup = acc.get_lineup_details()
        self.empty_lineup_position_ids  = [item['position_id'] for item in lineup if item.get('current') is None]
        if self.empty_lineup_position_ids:
            missing_player = True
        return missing_player
    
    def alternative_lineup_option(self):
        alternative_options = False
        lineup = acc.get_lineup_details()
        positions_ids_with_alternatives = [item['position_id'] for item in lineup if item.get('available') is not None]
        if positions_ids_with_alternatives:
            alternative_options = True
        return alternative_options
    
    def transfermarket_update(self):
        update = False
        try:
            with open(os.path.join(parent_dir, 'assets/old_transfermarket_offers.json'), 'r') as json_file:
                old_offers = json.load(json_file)
        except FileNotFoundError:
            old_offers = None
        
        if old_offers is not None:
            old_offer_ids = [item['id'] for item in old_offers]
        else:
            old_offer_ids = []

        actual_offers = acc.get_transfermarket_offers("buying")
        # print(actual_offers)
        actual_offer_ids = [item['id'] for item in actual_offers]
        self.new_transfermarket_offer_ids = list(set(actual_offer_ids)-set(old_offer_ids))

        filtered_offers = [objekt for objekt in actual_offers if objekt['id'] in self.new_transfermarket_offer_ids]
        self.new_player_ids = [obj["player"]["id"] for obj in filtered_offers]

        if any(actual_offer_id not in old_offer_ids for actual_offer_id in actual_offer_ids):
            update = True
            with open(os.path.join(parent_dir, 'assets/old_transfermarket_offers.json'), "w") as json_file:
                json.dump(actual_offers, json_file, indent=4)
        return update

if __name__ == '__main__':
    
    mnt = Monitor()
    # print(mnt.negative_balance())
    # print(mnt.missing_player_in_the_lineup())
    # print(mnt.alternative_lineup_option())
    # print(mnt.transfermarket_update())
    # print(mnt.new_player_ids)
