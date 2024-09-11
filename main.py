from utils import logger
from services import account, monitoring
from services import automation

logger.setup_logger()

acc = account.Account()
ntf = monitoring.Notificaton()
atm = automation.Automation()

login_bonus = acc.get_login_bonus()
print(login_bonus)