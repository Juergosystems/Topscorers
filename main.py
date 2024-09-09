from utils import logger
from services import account
from services import notification, automation

logger.setup_logger()

acc = account.Account()
ntf = notification.Notificaton()
atm = automation.Automation()

login_bonus = acc.get_login_bonus()
print(login_bonus)