from utils import logger
from services import account

logger.setup_logger()

acc = account.Account()

login_bonus = acc.get_login_bonus()
print(login_bonus)