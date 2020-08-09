EXTENSIONS = ["src.cogs.game", "src.cogs.manage"]
OWNER_ID = 226700060308668420
CMD_PREFIX = "!"

LONG_DESCRIPTIONS = {}

with open("./src/long_descriptions.txt", encoding="UTF-8") as f:
    d = f.readlines()

for line in d:
    if line.startswith("!"):
        des = ""
        cmd = line[1:].strip()
    elif line.startswith("$"):
        LONG_DESCRIPTIONS[cmd] = des.strip()
    else:
        des += line.replace("{CMD_PREFIX}", CMD_PREFIX)

ALLOWED_CHANNEL = [635398034469158914, 738655532709183551]
# test channel, gall discord channel
