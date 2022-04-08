#!/usr/bin/env python
# pylint: disable=C0116,W0613
# This program is dedicated to the public domain under the CC0 license.

"""
Bot to send you workout program
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""
import itertools
import logging
import os
import re
from typing import List

from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from telegram.utils.helpers import escape_markdown

from workout import create_training_plan

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

HELP_WITH_SUPPORTED_WORKOUTS = "Используй комманду /workout [ноги|спина|грудь] (+|,) (руки|плечи) (кол-во упражнений)"
DEFAULT_NUM_WORKOUTS = 5


# Define a few command handlers. These usually take the two arguments update and
# context.
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_markdown_v2(
        f'Привет {user.mention_markdown_v2()}\! Что сегодня треним?'
    )


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text(HELP_WITH_SUPPORTED_WORKOUTS)


def render_train_plan(requested_workouts: List[str], exercises: List[str]) -> str:
    if len(exercises) > 0:
        rendered_list = '\n'.join([f'{count + 1}. {value}' for count, value in enumerate(exercises)])
        return escape_markdown(f"План тренировки [{','.join(requested_workouts)}]:\n" + rendered_list, version=2)
    else:
        return escape_markdown(f"Не найдены тренировки [{','.join(requested_workouts)}].\n"
                               + HELP_WITH_SUPPORTED_WORKOUTS, version=2)


def workout_plan_command(update: Update, context: CallbackContext) -> None:
    numbers = []
    tokens = []
    for elem in context.args:
        if not re.match('[+,]', elem):
            numbers.append(elem) if elem.isnumeric() else tokens.append(elem)
    num_workouts = int(next(numbers.__iter__(), DEFAULT_NUM_WORKOUTS))
    requested_workouts = list(
        itertools.chain.from_iterable([re.split("\\s?[+,]\\s?", token.lower()) for token in tokens])
    )
    if len(requested_workouts) > 0:
        update.message.reply_markdown_v2(
            render_train_plan(requested_workouts, create_training_plan(requested_workouts, num_workouts))
        )
    else:
        update.message.reply_markdown_v2(
            escape_markdown("Нет типа тренировки в запросе.\n" + HELP_WITH_SUPPORTED_WORKOUTS, version=2)
        )


def echo(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""
    update.message.reply_text("Я могу помочь с программой упражнений.\n" + HELP_WITH_SUPPORTED_WORKOUTS)


def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(os.environ.get('TELEGRAM_TOKEN'))

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("workout", workout_plan_command))
    # Handle internal error

    # on non command i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
