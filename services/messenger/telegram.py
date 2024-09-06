import os
import sys

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print(parent_dir)
sys.path.append(parent_dir)

import requests
import json
from config import Config as cfg

class Telegram:

    def __init__(self):
        with open(os.path.join(parent_dir, 'telegram_credentials.json'), 'r') as file:
            self.credentials = json.load(file)

    def send_message(self, topic, body):
        push_message = cfg.ms.TELEGRAM_MESSAGE_BLUEPRINT.format(topic=topic, body=body)
        url=f"https://api.telegram.org/bot{self.credentials['token']}/sendMessage?chat_id={self.credentials['chatId']}&text={push_message}"
        return requests.get(url).json()

if __name__=='__main__':

    tlgm = Telegram()
    topic = "Missing Player!"
    body = "You are missing a defender in your roster for tonight's round."

    print(tlgm.send_message(topic, body))