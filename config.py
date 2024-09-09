class Config:

    class ts:

        BASIC_HEADERS = {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU OS 16_6 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/16.6 Mobile/10A5355d Safari/8536.25',
                'Content-Type': 'application/json;charset=utf-8',
                'Accept-Encoding': 'gzip, deflate, br',
                'X-Requested-With': 'XMLHttpRequest',
                'Accept': 'application/json, text/plain, */*'
            }
        USER_ID = 34636
        TEAM_ID = 227092
        LEAGUE_ID = 60198

    class ms:

        TELEGRAM_MESSAGE_BLUEPRINT = "{topic} \n \n{body}"

