# Topscorers

### Breaking Change

- renamed credentials.json to topscorer_credentials.json

### Manual

- create a topscorer_credentials.json file in the project root with one json object containing the keys "email" and "password" ({"email":"abc@x.yz", "password": "1234"}).
- Install all the required libraries from the requirements.txt (recommended: in a new virtual environment)
- run the get_login_bonus function daily to collect the login bonus.

- if you would like to build up on the new automations, then you need to create a telegram_credentials.json in the project root with one json object containing the keys "token" and "chatId" ({"token": "12345", "chatId": 12345"}).
