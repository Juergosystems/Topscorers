import json

def load_credentials():
    with open("topscorer_credentials.json", 'r') as file:
        return json.load(file)

credentials = load_credentials()

class Config:

    class ts:

        BASIC_HEADERS = {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU OS 16_6 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/16.6 Mobile/10A5355d Safari/8536.25',
                'Content-Type': 'application/json;charset=utf-8',
                'Accept-Encoding': 'gzip, deflate, br',
                'X-Requested-With': 'XMLHttpRequest',
                'Accept': 'application/json, text/plain, */*'
            }
        USER_ID = credentials['user_id']
        TEAM_ID = credentials['team_id']
        LEAGUE_ID = credentials['league_id']

    class intl:
        CURRENT_SEASON_SOCRING_WEIGHT = 10 # factor to increase the weight of the current season performance compared to last season in the scoring algorithm

    class atm:

        ALERT_OFFSET = 360000 # time in seconds till the next round to trigger alert

    class ms:

        TELEGRAM_MESSAGE_BLUEPRINT = "*{topic}* \n \n{body}"

    class ep:
        HEADERS = {
            "content-type": 'application/json'
        }

