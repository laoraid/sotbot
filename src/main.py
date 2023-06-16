from interactions import Intents
from interactions.ext import prefixed_commands

from src.classes.base import Sotbot
from src.vars import BOT_TOKEN, COMMAND_PREFIX

if __name__ == "__main__":
    intents = Intents.DEFAULT
    bot = Sotbot(
        activity="침몰",
        intents=Intents.DEFAULT | Intents.MESSAGE_CONTENT | Intents.GUILD_MESSAGES,
        send_command_tracebacks=False,
        sync_interactions=True,
        delete_unused_application_cmds=True,
    )
    prefixed_commands.setup(bot, default_prefix=COMMAND_PREFIX)
    bot.load_extensions()
    bot.start(token=BOT_TOKEN)
