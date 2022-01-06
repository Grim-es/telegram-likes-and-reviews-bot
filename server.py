import os
import logging
from typing import Union

from telegram import KeyboardButton
from telegram import ReplyKeyboardMarkup
from telegram import Update
from telegram.ext import CallbackContext
from telegram.ext import CallbackQueryHandler
from telegram.ext import CommandHandler
from telegram.ext import ConversationHandler
from telegram.ext import Filters
from telegram.ext import MessageHandler
from telegram.ext import Updater

import reviews
import users
import utils

API_TOKEN = os.getenv('TG_API_KEY')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

callbacks = {
    'rate': utils.update_rating,
    'review': utils.request_review,
    'get_reviews': utils.get_reviews,
    'delete': utils.delete_review,
    'cancel': utils.cancel_review
}

insturctions = 'To search for users, enter First Name and Last Name\n' \
               'You will be shown a user of your choice, to whom you can leave a review and rate'


def start(update: Update, context: CallbackContext) -> None:
    """Sends a welcome message and bot help"""
    utils.send_message(update=update, context=context, text=f"Instructions:\n{insturctions}")


def not_authorized(update: Update, context: CallbackContext) -> str:
    """Requests the user's full name"""
    utils.send_message(update=update, context=context,
                       text=f"Authorization is required, enter First Name and Last Name")
    return 'NAME'


def search(update: Update, context: CallbackContext) -> None:
    """Parses the list of users by search criteria"""
    values = update.message.text.split()
    found_users = users.get_users(values)
    if not found_users:
        utils.send_message(update=update, context=context, text=f"User is not found: {' '.join(values)}\n"
                                                                f"{insturctions}")
        return

    for user in found_users:
        utils.send_user_info(update=update, context=context, user=user)
    return


def unknown(update: Update, context: CallbackContext) -> None:
    """Unknown command handler"""
    utils.send_message(update=update, context=context, text="Unknown command entered")


def button_callback(update: Update, context: CallbackContext) -> Union[None, str]:
    """Callback request handler"""
    query = update.callback_query
    query.answer()
    message = query.data.split()
    return callbacks[message[0]](update=update, context=context, query=query, message=message)


def request_full_name(update: Update, context: CallbackContext) -> str:
    """Requests the user's phone number"""
    values = update.message.text.split()
    if len(values) != 3:
        utils.send_message(update=update, context=context,
                           text="Incorrect data entered, please enter First Name and Last Name")
        return 'NAME'

    context.user_data['user'] = {
        'id': update.effective_chat.id,
        'name': values[0],
        'last_name': values[1]
    }

    keyboard = [[KeyboardButton("Share phone number", request_contact=True)]]
    reply_markup = ReplyKeyboardMarkup(keyboard)
    utils.send_message(update=update, context=context, text="Now enter your phone number", reply_markup=reply_markup)
    return 'PHONE'


def request_phone(update: Update, context: CallbackContext) -> str:
    """Requests user photo"""
    if update.message.text:
        utils.send_message(update=update, context=context,
                           text="In order to share your phone number, click on the corresponding button")
        return 'PHONE'

    context.user_data['user']['phone_number'] = update.message.contact.phone_number
    utils.send_message(update=update, context=context, text="Good, now send a photo for your profile")
    return 'PHOTO'


def request_photo_and_submit(update: Update, context: CallbackContext) -> Union[str, int]:
    """Enters information about the user into the database"""
    if update.message.text or update.message.document:
        utils.send_message(update=update, context=context,
                           text="You need to send a photo for your profile ")
        return 'PHOTO'

    utils.add_user(update=update, context=context)
    utils.send_message(update=update, context=context, text="Registration completed successfully")
    utils.send_message(update=update, context=context, text=f"Instructions:\n{insturctions}")
    return ConversationHandler.END


def submit_review(update: Update, context: CallbackContext) -> int:
    """Fills user feedback in the database"""
    from_user = update.effective_chat
    reviews.add_review(user_id=context.user_data['user_id'], from_id=from_user.id,
                       message=f'{from_user.first_name} {from_user.last_name} @{from_user.username}\n'
                               f'{update.message.text}')
    del context.user_data['user_id']
    utils.send_message(update=update, context=context, text="Your review has been recorded")
    return ConversationHandler.END


def main() -> None:
    """The main function of launching the bot"""
    updater = Updater(token=API_TOKEN, use_context=True)

    dispatcher = updater.dispatcher

    # authorization callback
    authorization_conv = ConversationHandler(
        entry_points=[MessageHandler(utils.FilterNotAuthorized(), not_authorized)],
        states={
            'NAME': [MessageHandler(Filters.text & ~Filters.command, request_full_name)],
            'PHONE': [MessageHandler((Filters.text | Filters.contact) & ~Filters.command, request_phone)],
            'PHOTO': [MessageHandler((Filters.text | Filters.photo | Filters.document) & ~Filters.command,
                                     request_photo_and_submit)]
        },
        fallbacks=[CallbackQueryHandler(button_callback, pattern='^registered')]
    )

    # review callback
    review_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_callback, pattern='^review')],
        states={'SUBMIT': [MessageHandler(Filters.text & ~Filters.command, submit_review)]},
        fallbacks=[CallbackQueryHandler(button_callback, pattern='^cancel')]
    )

    # button callbacks
    dispatcher.add_handler(authorization_conv)
    dispatcher.add_handler(review_conv)
    dispatcher.add_handler(CallbackQueryHandler(button_callback, pattern='^(rate|get_reviews|delete)'))

    # commands
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, search))
    dispatcher.add_handler(MessageHandler(Filters.command, unknown))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
