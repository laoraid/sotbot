import logging
import os

from .classes.mylogger import botlogger

OWNER_ID = 226700060308668420
COMMAND_PREFIX = "!"

try:
    BOT_TOKEN = os.environ["BOT_TOKEN"]
    DEBUG_MODE = False
except KeyError:
    from . import bottoken

    BOT_TOKEN = bottoken.TOKEN

    botlogger.setLevel(logging.DEBUG)

    DEBUG_MODE = True

ALLOWED_CHANNEL = [1118787842408202290]
# test channel

if not DEBUG_MODE:
    ALLOWED_CHANNEL = [1115325402831929394, 745498767117254676]
    # gall discord channel, bot manage channel

ID_CHANGE_CHANNEL = 1115339731790733364

SCOPES = [635398034469158912, 1114918248253759648]
