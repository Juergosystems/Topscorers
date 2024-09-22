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
from config import Config as cfg
from utils.logger import logger

class CustomTelegram:

    def __init__(self):
        try:
            with open(os.path.join(parent_dir, 'telegram_credentials.json'), 'r') as file:
                self.credentials = json.load(file)
        
        except Exception as e:
            logger.error(f'Ein Fehler ist aufgetreten: {e}')

    def send_message(self, topic, body):
        try:
            push_message = cfg.ms.TELEGRAM_MESSAGE_BLUEPRINT.format(topic=topic, body=body)
            url=f"https://api.telegram.org/bot{self.credentials['token']}/sendMessage?chat_id={self.credentials['chatId']}&text={push_message}&parse_mode=Markdown"
            return requests.get(url).json()
        
        except Exception as e:
            logger.error(f'Ein Fehler ist aufgetreten: {e}')

    # Funktion zum Beenden des Bots
    def __stop_bot(self, context):
        # Beendet den Bot-Prozess
        context.application.stop_running()
        context.application.shutdown()
        print("Bot stopped.")


    def __stop_bot_with_params(self, context=None):
        async def stop(context=context) -> None:
            # Beendet den Bot-Prozess
            context.application.stop_running()
            context.application.shutdown()
            print("Bot stopped.")
        return stop
        

    # Start-Nachricht mit Inline-Buttons
    def __start_with_params(self, initial_question, chatId=None):
        async def start(context) -> None:
            keyboard = [
                [InlineKeyboardButton("Yes", callback_data='yes'), 
                InlineKeyboardButton("No", callback_data='no')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await context.bot.send_message(chat_id=chatId, text=initial_question, reply_markup=reply_markup)
        return start

    # Callback-Handler für die Inline-Button-Auswahl
    def __button_with_params(self, yes_text, no_text):
        async def button(update: Update, context) -> None:
            query = update.callback_query
            await query.answer()

            if query.data == 'yes':
                sent_message = await query.edit_message_text(text=yes_text)
                context.user_data['bid_message_id'] = sent_message.message_id
                print(context.user_data['bid_message_id'])
            elif query.data == 'no':
                await query.edit_message_text(text=no_text)
                context.user_data['bid_message_id'] = None
                self.__stop_bot(context)
                print("Bot stopped because 'No' was selected.")
                
        return button

    # Nachrichten-Handler für die Eingabe des Gebots
    async def __handle_message(self, update: Update, context) -> None:
        if update.message.reply_to_message and update.message.reply_to_message.message_id == context.user_data.get('bid_message_id'):
            try:
                bid = int(update.message.text)
                await update.message.reply_text(f'Your bid is: {bid}')
                self.__stop_bot(context)
                print("Bot stopped after receiving a valid bid.")
                
            except ValueError:
                await update.message.reply_text('Please provide a valid number for the bid.')
        else:
            await update.message.reply_text('Please reply to the bid message to submit your bid.')
                                      
    def send_biding_request(self, initial_question, yes_text, no_text):

        BOT_LIFETIME = 10  # 24 Stunden in Sekunden
        application = Application.builder().token(cfg.ms.TELEGRAM_TOKEN).build()

        # Callback-Handler für die Inline-Button-Auswahl
        application.add_handler(CallbackQueryHandler(self.__button_with_params(yes_text=yes_text, no_text=no_text)))

        # Nachrichten-Handler für Geboteingaben
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.__handle_message))

        job_queue = application.job_queue
        job_queue.run_once(callback=self.__start_with_params(initial_question=initial_question, chatId=cfg.ms.TELEGRAM_CHAT_ID), when=0)
        job_queue.run_once(callback=self.__stop_bot_with_params(context=None), when=24*60*60)  # 24 Stunden Verzögerung

        # Starten des Bots
        application.run_polling()

        return 10







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