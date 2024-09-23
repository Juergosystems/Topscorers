import os
import sys
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
import threading
import asyncio


parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(parent_dir)
sys.path.append(parent_dir)

import requests
import json
from services import account
from config import Config as cfg
from utils.logger import logger

acc = account.Account()

class CustomTelegram:

    def __init__(self):
        try:
            with open(os.path.join(parent_dir, 'telegram_credentials.json'), 'r') as file:
                self.credentials = json.load(file)
            self.number_of_bids = None
            self.job_queue = None
            
        
        except Exception as e:
            logger.error(f'Ein Fehler ist aufgetreten: {e}')

    def send_message(self, topic, body):
        try:
            push_message = cfg.ms.TELEGRAM_MESSAGE_BLUEPRINT.format(topic=topic, body=body)
            url=f"https://api.telegram.org/bot{self.credentials['token']}/sendMessage?chat_id={self.credentials['chatId']}&text={push_message}&parse_mode=Markdown"
            return requests.get(url).json()
        
        except Exception as e:
            logger.error(f'Ein Fehler ist aufgetreten: {e}')

    def __stop_bot_with_params(self, context=None):
        async def stop(context=context) -> None:
            # Beendet den Bot-Prozess
            for key in list(context.bot_data.keys()):
                await context.bot.delete_message(chat_id=cfg.ms.TELEGRAM_CHAT_ID, message_id=int(key))
            context.application.stop_running()
            context.application.shutdown()
            print("Bot stopped as the bid requests were expired.")
        return stop
        

    # Start-Nachricht mit Inline-Buttons
    def __start_with_params(self, initial_question, chatId=None):
        async def start(context) -> None:
            keyboard = [
                [InlineKeyboardButton("Yes", callback_data='yes'), 
                InlineKeyboardButton("No", callback_data='no')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            sent_message = await context.bot.send_message(chat_id=chatId, text=initial_question, reply_markup=reply_markup)
            context.bot_data[str(sent_message.message_id)] = context.job.data

        return start

    # Callback-Handler für die Inline-Button-Auswahl
    def __button_with_params(self, yes_text, no_text):
        async def button(update: Update, context) -> None:
            query = update.callback_query
            await query.answer()
            initial_message_ide = str(query.message.message_id)
            player = context.bot_data[initial_message_ide]
            if query.data == 'yes':
                sent_message = await query.edit_message_text(text=yes_text.format(player_name=player["name"]))
                context.user_data[str(sent_message.message_id)] = player

            elif query.data == 'no':
                await query.edit_message_text(text=no_text.format(player_name=player["name"]))
                context.user_data['bid_message_id'] = None
                 
        return button

    # Nachrichten-Handler für die Eingabe des Gebots
    async def __handle_message(self, update: Update, context) -> None:
        if update.message.reply_to_message:
            try:
                corresponding_message_id = str(update.message.reply_to_message.message_id)
                player = context.user_data[corresponding_message_id]
                bid = int(update.message.text)
                acc.place_bid(offer_id=player["offer_id"], price=bid)
                await update.message.reply_text(f'Your bid for {player["name"]} is: {bid}')
                
            except ValueError:
                await update.message.reply_text('Please provide a valid number for the bid.')
        else:
            await update.message.reply_text('Please reply to the bid message to submit your bid.')
                                      
    def send_biding_notification(self, alerting_players):

        initial_questions = []
        for player in alerting_players:
            initial_questions.append(f"There is a new interesting player on the market: \n" + f" •  {player['name']}" + f", {player['team']}\n" + f"    {player['marketValue']:,}".replace(",","'") + f" CHF, trend: {player['marketValueTrend']} \n\nWould you like to bid?")

        yes_text = "What is your bid for {player_name}? Reply to this message with your bid."
        no_text = "Okay, no bid for {player_name}."

        self.number_of_bids = len(alerting_players)
        application = Application.builder().token(cfg.ms.TELEGRAM_TOKEN).build()

        application.add_handler(CallbackQueryHandler(self.__button_with_params(yes_text=yes_text, no_text=no_text)))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.__handle_message))

        self.job_queue = application.job_queue
        for index, player in enumerate(alerting_players):
            self.job_queue.run_once(callback=self.__start_with_params(initial_question=initial_questions[index], chatId=cfg.ms.TELEGRAM_CHAT_ID), data=player, when=1)
        self.job_queue.run_once(callback=self.__stop_bot_with_params(context=None), when=cfg.atm.TRANSFERMARKET_ALERT_OFFSET)  # automatisches abstellen des Bots nach einer gewissen Zeit

        application.run_polling()

        return







if __name__=='__main__':

    tlgm = CustomTelegram()
    topic = "Missing Player!"
    body = "You are missing a defender in your roster for tonight's round."

    # print(tlgm.send_message(topic, body))

    initial_question = "Shall I bid?"
    yes_text = "What is your bid? Reply to this message with your bid."
    no_text = "Okay, no bid."

    print(tlgm.send_biding_request(initial_question, yes_text, no_text))

    print(5)