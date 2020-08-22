from discord.ext import commands, tasks

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @tasks.loop(hours=1)
    async def twitch_drops_loop(self):
        DROPSURL = "https://www.seaofthieves.com/ko/twitch-drops"
        async with aiohttp.ClientSession() as session:
            async with session.get(DROPSURL) as res:



def setup(bot):
    bot.add_cog(Events(bot))