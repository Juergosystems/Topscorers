import os
import sys
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
import threading
import asyncio


parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(parent_dir)
sys.path.append(parent_dir)

import requests
import json
from services import account
from config import Config as cfg
from utils.logger import logger
import ast

acc = account.Account()

class TelegramHelper:

    def __init__(self):
        try:
            with open(os.path.join(parent_dir, 'telegram_credentials.json'), 'r') as file:
                self.credentials = json.load(file)
            self.number_of_bids = None
            self.job_queue = None
            
        
        except Exception as e:
            logger.error(f'Ein Fehler ist aufgetreten: {e}')

    def send_message(self, topic, body):
        try:
            push_message = cfg.ms.TELEGRAM_MESSAGE_BLUEPRINT.format(topic=topic, body=body)
            url=f"https://api.telegram.org/bot{self.credentials['token']}/sendMessage?chat_id={self.credentials['chatId']}&text={push_message}&parse_mode=Markdown"
            return requests.get(url).json()
        
        except Exception as e:
            logger.error(f'Ein Fehler ist aufgetreten: {e}')

    def send_biding_request(self, player):
        request_type = "bid"
        try:
            request_topic = f"There is a new interesting player on the market!" 
            request_body = f" •  {player['name']}" + f", {player['team']}\n" + f"    {player['marketValue']:,}".replace(",","'") + f" CHF, trend: {player['marketValueTrend']} \n\nWould you like to bid?"
            request_message = cfg.ms.TELEGRAM_MESSAGE_BLUEPRINT.format(topic=request_topic, body=request_body)
            reply_markup_yes =f'{{"answer":"yes", "type":"{request_type}", "offer_id": "{player["offer_id"]}"}}' 
            reply_markup_no =f'{{"answer":"no", "type":"{request_type}", "offer_id": "{player["offer_id"]}"}}'
            reply_markup =  json.dumps({"inline_keyboard":[[{"text":"Yes","callback_data":reply_markup_yes},{"text":"No","callback_data":reply_markup_no}]]})
            
            url = f"https://api.telegram.org/bot{cfg.ms.TELEGRAM_TOKEN}/sendMessage?chat_id={cfg.ms.TELEGRAM_CHAT_ID}&text={request_message}&reply_markup={reply_markup}&parse_mode=Markdown"

            return requests.get(url).json()
        
        except Exception as e:
            logger.error(f'Ein Fehler ist aufgetreten: {e}')

    
    
if __name__=='__main__':

    tlgm = TelegramHelper()

    player =     {
                    "id": 155486,
                    "name": "Denis Malgin",
                    "team": "ZSC Lions",
                    "position": "Forward",
                    "score": 0.9984047753323465,
                    "marketValue": 795885,
                    "marketValueTrend": 1,
                    "inLiveLineup": True,
                    "offer_id": 101342795,
                    "expires_in": 27760
                }
    
    tlgm.send_biding_request(player)
