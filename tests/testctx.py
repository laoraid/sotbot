from datetime import datetime

import discord


class message(object):
    def __init__(self, msg):
        self.content = msg
        self.created_at = datetime.utcnow()


class ctx(object):
    def __init__(self):
        self.lastsend = ""
        self.lastembed: discord.Embed = None
        self.message = message("IT IS TEST")

    async def send(self, s=None, *, embed=None):
        self.lastsend = s
        self.lastembed = embed
        self.message = message(s)
