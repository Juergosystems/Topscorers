from utils import logger, telegram_helper
from services import account, monitoring
from services import automation

logger.setup_logger()

atm = automation.Automation()
tlgm = telegram_helper.TelegramHelper()

try:
    atm.bonus_handler(mode="automated")
except Exception as e:
    topic = "Error!"
    message = f'Ein Fehler im Bonus Handler ist aufgetreten: {e}'
    logger.error(message)
    tlgm.send_message(topic, message)

try:
    atm.balance_handler(mode="info")
except Exception as e:
    topic = "Error!"
    message = f'Ein Fehler im Balance Handler ist aufgetreten: {e}'
    logger.error(message)
    tlgm.send_message(topic, message)

try:
    atm.lineup_handler(mode="automated")
except Exception as e:
    topic = "Error!"
    message = f'Ein Fehler im Lineup Handler ist aufgetreten: {e}'
    logger.error(message)
    tlgm.send_message(topic, message)

try:
    atm.transfermarket_handler(mode="info")
except Exception as e:
    logger.error(f'Ein Fehler im Transfermarket Handler ist aufgetreten: {e}')
    topic = "Error!"
    message = f'Ein Fehler im Transfermarket Handler ist aufgetreten: {e}'
    logger.error(message)
    tlgm.send_message(topic, message)
