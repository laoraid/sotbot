from datetime import datetime

import discord


class message(object):
    def __init__(self, msg, ca=None):
        self.content = msg
        if ca is not None:
            self.created_at = ca
        else:
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
