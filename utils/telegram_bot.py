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
import ast

acc = account.Account()

class TelegramBot:

    # Handler für abgelaufene Transfermarket offers
    def __delete_bid_request_after_expiration(self, message_id, offer_id, context=None):
        async def delete_message(context=context) -> None:
            await context.bot.delete_message(chat_id=cfg.ms.TELEGRAM_CHAT_ID, message_id=int(message_id))
            print("Offer ", offer_id, " expired.")
        return delete_message

    # Callback-Handler für die Inline-Button-Auswahl
    def __button_with_params(self, yes_text, no_text):
        async def button(update: Update, context) -> None:
            
            query = update.callback_query
            await query.answer()
            initial_message_id = query.message.message_id
            query_data = ast.literal_eval(query.data)

            if query_data["type"] == "bid":
                offer_id = query_data["offer_id"]
                transfermarket_offers = acc.get_transfermarket_offers("buying")
                for offer in transfermarket_offers:
                    if offer['id'] == int(offer_id):
                        player = offer['player']
                        query_data["player_id"] = player['id']
                        query_data["name"] = f"{player['firstname']} {player['lastname']}"
            
                job_queue = context.application.job_queue
                job_queue.run_once(callback=self.__delete_bid_request_after_expiration(message_id=initial_message_id, offer_id=query_data["offer_id"],context=None), when=cfg.atm.TRANSFERMARKET_ALERT_OFFSET)

                if query_data["answer"] == 'yes':
                    sent_message = await query.edit_message_text(text=yes_text.format(player_name=query_data["name"]))
                    context.user_data[str(sent_message.message_id)] = query_data

                elif query_data["answer"] == 'no':
                    print("No bid placed for ",query_data["name"])
                    await query.edit_message_text(text=no_text.format(player_name=query_data["name"]))
                    context.user_data['bid_message_id'] = None
            else:
                return
                 
        return button

    # Nachrichten-Handler für die Eingabe des Gebots
    async def __handle_message(self, update: Update, context) -> None:
        if update.message.reply_to_message:
            try:
                corresponding_message_id = str(update.message.reply_to_message.message_id)
                query_data = context.user_data[corresponding_message_id]
                
                if query_data["type"] == "bid":
                    bid = int(update.message.text)
                    acc.place_bid(offer_id=query_data["offer_id"], price=bid)
                    print("Bid of ", bid, "placed for ", query_data["name"])
                    await update.message.reply_text(f'Your bid of {bid} for {query_data["name"]} has been placed.')
                else:
                    return
                
            except ValueError:
                await update.message.reply_text('Please provide a valid input.')
        else:
            return
                                      
    def start_bot(self):

        yes_text = "What is your bid for {player_name}? Reply to this message with your bid."
        no_text = "Okay, no bid for {player_name}."

        application = Application.builder().token(cfg.ms.TELEGRAM_TOKEN).build()

        application.add_handler(CallbackQueryHandler(self.__button_with_params(yes_text=yes_text, no_text=no_text)))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.__handle_message))

        application.run_polling()

        return







if __name__=='__main__':

    tlgm = TelegramBot()

    tlgm.start_bot()
