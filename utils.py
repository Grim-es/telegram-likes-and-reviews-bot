import base64
import io
from typing import List
from typing import Optional
from typing import Union

from telegram import CallbackQuery
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup
from telegram import ReplyKeyboardMarkup
from telegram import Update
from telegram.ext import CallbackContext
from telegram.ext import ConversationHandler
from telegram.ext import MessageFilter

import rating
import reviews
import users


def send_message(update: Update, context: CallbackContext, text: str, photo: Optional[bytes] = None,
                 reply_markup: Optional[Union[InlineKeyboardMarkup, ReplyKeyboardMarkup]] = None) -> None:
    """Sends message, photo and built-in keyboard"""
    if photo:
        context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo, caption=text, reply_markup=reply_markup)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text=text, reply_markup=reply_markup)


def add_user(update: Update, context: CallbackContext) -> None:
    """Enters information about the user into the database"""
    data = context.user_data['user']

    photo_stream = io.BytesIO()
    update.message.photo[-1].get_file().download(out=photo_stream)
    photo = base64.b64encode(photo_stream.getvalue())

    users.add_user(
        user_id=data['id'],
        name=data['name'],
        last_name=data['last_name'],
        phone_number=data['phone_number'],
        photo=photo.decode()
    )
    del context.user_data['user']


def send_user_info(update: Update, context: CallbackContext, user: users.User) -> None:
    """Sends a user card"""
    user_info = f"{user.name} {user.last_name}"
    user_photo = base64.b64decode(user.photo) if user.photo else None
    reply_markup = get_user_markup(user_id=user.id)
    send_message(update=update, context=context, text=user_info, photo=user_photo, reply_markup=reply_markup)


def get_user_markup(user_id: int) -> InlineKeyboardMarkup:
    """Generates a built-in keyboard for a user card"""
    user_rating = rating.get_user_rating(user_id)

    likes = sum([int(rate.likes) for rate in user_rating])
    dislikes = sum([int(rate.dislikes) for rate in user_rating])

    keyboard = [
        [
            InlineKeyboardButton(f"👍 {likes}", callback_data=f'rate {user_id} likes'),
            InlineKeyboardButton(f"👎 {dislikes}", callback_data=f'rate {user_id} dislikes'),
        ],
        [InlineKeyboardButton("Leave review", callback_data=f'review {user_id}')],
        [InlineKeyboardButton("View reviews", callback_data=f'get_reviews {user_id}')]
    ]
    return InlineKeyboardMarkup(keyboard)


def update_rating(update: Update, query: CallbackQuery, message: List[str], **_) -> None:
    """Changes the user's rating and updates his card"""
    user_id = int(message[1])
    rating.update_rating(user_id=user_id, from_id=update.effective_chat.id, rate=message[2] == "likes")
    reply_markup = get_user_markup(user_id=user_id)
    query.edit_message_reply_markup(reply_markup)


def request_review(update: Update, context: CallbackContext, message: List[str], **_) -> str:
    """Requests user feedback"""
    context.user_data['user_id'] = message[1]
    keyboard = [[InlineKeyboardButton("Cancel", callback_data='cancel')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    send_message(update=update, context=context, text="Write the review you want to leave",
                 reply_markup=reply_markup)
    return 'SUBMIT'


def get_reviews(update: Update, context: CallbackContext, message: List[str], **_) -> None:
    """Submits all user reviews"""
    user_reviews = reviews.get_reviews(user_id=int(message[1]))
    if not user_reviews:
        send_message(update=update, context=context, text="There are no reviews for this user")
        return

    for review in user_reviews:
        reply_markup = get_review_markup(update=update, review=review)
        send_message(update=update, context=context, text=review.message, reply_markup=reply_markup)


def delete_review(query: CallbackQuery, message: List[str], **_) -> None:
    """Removes user feedback and message"""
    reviews.delete_review(int(message[1]))
    query.delete_message()


def cancel_review(context: CallbackContext, query: CallbackQuery, **_) -> str:
    """Cancels the request and deletes the message"""
    query.delete_message()
    del context.user_data['user_id']
    return ConversationHandler.END


def get_review_markup(update: Update, review: reviews.Review) -> Union[InlineKeyboardMarkup, None]:
    """Generates a built-in keyboard for user feedback"""
    reply_markup = None
    if update.effective_chat.id == review.from_id:
        keyboard = [[InlineKeyboardButton("Delete", callback_data=f'delete {review.id}')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup


class FilterNotAuthorized(MessageFilter):
    """Filter to check if the user is authorized"""
    def filter(self, message):
        return not users.get_user(message.chat_id)
