import json

def load_credentials(file):
    with open(file, 'r') as file:
        return json.load(file)

ts_credentials_file = "topscorer_credentials.json"
tlgm_credentials_file = "telegram_credentials.json"

ts_credentials = load_credentials(ts_credentials_file)
tlgm_credentials = load_credentials(tlgm_credentials_file)

class Config:

    class ts:

        BASIC_HEADERS = {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU OS 16_6 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/16.6 Mobile/10A5355d Safari/8536.25',
                'Content-Type': 'application/json;charset=utf-8',
                'Accept-Encoding': 'gzip, deflate, br',
                'X-Requested-With': 'XMLHttpRequest',
                'Accept': 'application/json, text/plain, */*'
            }
        
        USER_ID = ts_credentials['user_id']
        TEAM_ID = ts_credentials['team_id']
        LEAGUE_ID = ts_credentials['league_id']

    class intl:
        
        CURRENT_SEASON_SOCRING_WEIGHT = 5 # factor to increase the weight of the current season performance compared to last season in the scoring algorithm

    class atm:
        NEXT_ROUND_ALERT_OFFSET = 0.5 * 60 * 60 # time in seconds till the next round to trigger alert
        TRANSFERMARKET_ALERT_OFFSET = 10 * 60 * 60 # time for transfermarket alert before offer expires
        TRANSFERMARKET_ALERT_SCORE = 0.8 # only players with a higher score create an alert OR
        TRANSFERMAKRET_ALERT_TREND = [1] # only players with a market value trend included in the list create an alert OR
        TRANSFERMAKRET_ALERT_FAVORITE_TEAMS = ["ZSC Lions","EV Zug", "HC Lugano"] # only players from a specfic team create an alert



    class ms:

        TELEGRAM_MESSAGE_BLUEPRINT = "*{topic}* \n \n{body}"
        TELEGRAM_TOKEN = tlgm_credentials["token"]
        TELEGRAM_CHAT_ID = tlgm_credentials["chatId"]

    class ep:
        
        HEADERS = {
            "content-type": 'application/json'
        }

    class nl:
        
        HEADERS = {
            "content-type": 'application/json'
        }

