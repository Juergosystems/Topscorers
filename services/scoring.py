import os
import sys
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from utils.logger import logger
from utils import telegram
from services import account, notification
from config import Config

tlgm = telegram.Telegram()
acc = account.Account()
ntf = notification.Notificaton()


class Scoring:
    
    def __init__(self):
        return
    
