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
    def __button_with_params_for_bid_request(self, yes_text_new_bid, yes_text_existing_bid, no_text):
        async def button(update: Update, context) -> None:
            
            query = update.callback_query
            await query.answer()
            initial_message_id = query.message.message_id
            query_data = ast.literal_eval(query.data)

            if query_data["type"] == "bid":
                offer_id = query_data["offer_id"]
                offer_expired = True
                transfermarket_offers = acc.get_transfermarket_offers("buying")
                for offer in transfermarket_offers:
                    if offer['id'] == int(offer_id):
                        query_data["player_id"] = offer['player']['id']
                        query_data["name"] = f"{offer['player']['firstname']} {offer['player']['lastname']}"
                        query_data["market_value"] = offer['player']['marketvalue']
                        query_data["expires_in"] = offer["expires_in"]
                        try:
                            query_data["existing_bid_id"] = offer["offers"][0]["id"]
                            query_data["existing_bid"] = offer["offers"][0]["price"]
                        except:
                            query_data["existing_bid_id"] = 0
                        offer_expired = False
                        break
                
                job_queue = context.application.job_queue

                if offer_expired:
                    await query.edit_message_text(text=f'Offer {offer_id} is expired.')
                    job_queue.run_once(callback=self.__delete_bid_request_after_expiration(message_id=initial_message_id, offer_id=offer_id,context=None), when=10)
                    return

                job_queue.run_once(callback=self.__delete_bid_request_after_expiration(message_id=initial_message_id, offer_id=offer_id,context=None), when=query_data["expires_in"])

                if query_data["answer"] == 'yes' and query_data["existing_bid_id"] == 0:
                    sent_message = await query.edit_message_text(text=yes_text_new_bid.format(player_name=query_data["name"], marketvalue=(f'{query_data["market_value"]:,} CHF'.replace(",","'"))))
                    context.user_data[str(sent_message.message_id)] = query_data

                elif query_data["answer"] == 'yes':
                    sent_message = await query.edit_message_text(text=yes_text_existing_bid.format(player_name=query_data["name"], bid=(f'{query_data["existing_bid"]:,} CHF'.replace(",","'"))))
                    context.user_data[str(sent_message.message_id)] = query_data

                elif query_data["answer"] == 'no':
                    print("No bid placed for",query_data["name"])
                    await query.edit_message_text(text=no_text.format(player_name=query_data["name"]))
                    context.user_data['bid_message_id'] = None
            else:
                return
                 
        return button

    # Nachrichten-Handler für die Eingabe des Gebots
    async def __handle_message_for_bid_request(self, update: Update, context) -> None:
        if update.message.reply_to_message:
            try:
                corresponding_message_id = str(update.message.reply_to_message.message_id)
                query_data = context.user_data[corresponding_message_id]
                
                if query_data["type"] == "bid":
                    
                    offer_id = query_data["offer_id"]
                    bid_id = query_data["existing_bid_id"]
                    bid = int(update.message.text)

                    response_code, response_text = acc.place_bid(offer_id=query_data["offer_id"], price=bid)
                    if response_code == 200:
                        print("Bid of ", bid, "placed for ", query_data["name"])
                        await update.message.reply_text(f'Your bid of {bid:,} CHF for {query_data["name"]} has been placed.'.replace(",","'"))
                    elif query_data["existing_bid_id"] != 0 and bid != 0:
                        response_code, response_text = acc.update_bid(offer_id=offer_id, bid_id=bid_id, price=bid)
                        if response_code == 200:
                            print("Bid for", query_data["name"], "updated to", bid)
                            await update.message.reply_text(f'Your bid for {query_data["name"]} has been updated to {bid:,} CHF.'.replace(",","'"))
                        else:
                            await update.message.reply_text(f'We could not upaded your bid for {query_data["name"]}. Because: \n{response_text}')
                            print(response_code, ": ", response_text)
                    elif query_data["existing_bid_id"] != 0 and bid == 0:
                        response_code, response_text = acc.delete_bid(offer_id=offer_id, bid_id=bid_id)
                        if response_code == 200:
                            print("Bid for", query_data["name"], "deleted.")
                            await update.message.reply_text(f'Your bid for {query_data["name"]} has been deleted.')
                        else:
                            await update.message.reply_text(f'We could not delete your bid for {query_data["name"]}. Because: \n{response_text}')
                            print(response_code, ": ", response_text)
                    else:
                        await update.message.reply_text(f'We could not set your bid for {query_data["name"]}. Because: \n{response_text}')
                        print(response_code, ": ", response_text)
                else:
                    return
            except ValueError as e:
                await update.message.reply_text('Please provide a valid input.', e)
        else:
            return
                                      
    def start_bot(self):

        yes_text_new_bid = "What is your bid for {player_name} (marketvalue: {marketvalue})? Reply to this message with your bid."
        yes_text_existing_bid = "There is already a bid of {bid} for {player_name}. Reply to this message to update your bid. A bid of 0 will delete the current bid."
        no_text = "Okay, no bid for {player_name}."

        application = Application.builder().token(cfg.ms.TELEGRAM_TOKEN).build()

        application.add_handler(CallbackQueryHandler(self.__button_with_params_for_bid_request(yes_text_new_bid=yes_text_new_bid, yes_text_existing_bid=yes_text_existing_bid ,no_text=no_text)))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.__handle_message_for_bid_request))

        application.run_polling()

        return







if __name__=='__main__':

    tlgm = TelegramBot()

    tlgm.start_bot()
