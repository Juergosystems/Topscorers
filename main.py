from utils import logger
from services import account, monitoring
from services import automation

logger.setup_logger()

acc = account.Account()
ntf = monitoring.Monitor()
atm = automation.Automation()

acc.get_login_bonus()