from utils import logger
from services import account, monitoring
from services import automation

logger.setup_logger()

atm = automation.Automation()

atm.bonus_handler(mode="automated")
atm.balance_handler(mode="info")
atm.lineup_handler(mode="automated")
