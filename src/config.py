import os

EXTENSIONS = ["src.cogs.game", "src.cogs.manage", "src.cogs.server"]
OWNER_ID = 226700060308668420
CMD_PREFIX = "!"

LONG_DESCRIPTIONS = {}

with open("./src/long_descriptions.txt", encoding="UTF-8") as f:
    d = f.readlines()

for line in d:
    if line.startswith("!"):
        des = []
        cmd = line[1:].strip()
    elif line.startswith("$"):
        LONG_DESCRIPTIONS[cmd] = "".join(des).strip()
    else:
        des.append(line.replace("{CMD_PREFIX}", CMD_PREFIX))


try:
    BOT_TOKEN = os.environ['BOT_TOKEN']
    DEBUG_MODE = False
except KeyError:
    from . import bottoken
    BOT_TOKEN = bottoken.TOKEN
    DEBUG_MODE = True


ALLOWED_CHANNEL = [635398034469158914]
# test channel
CATEGORIES = {635398034469158912: [
    744122161765154827, 744122302869930075, 744122181696356414]}
ADD_CATEGORIES = {635398034469158912: [
    744213052622372915, 744213085761437727, 744213118942707722]}

if not DEBUG_MODE:
    ALLOWED_CHANNEL.append(738655532709183551)
    # gall discord channel
    CATEGORIES[725968832933527573] = [
        727357382916702279, 727357340784787506, 727357296333684794]
    ADD_CATEGORIES[725968832933527573] = [
        744221925663965306, 744221861730189402, 744221780033536040]
# CATEGORIES => Guild ID : [Galleon, brigantine, sloop categories id]
