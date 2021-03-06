import datetime
import re

import aiohttp
import wikitextparser
from discord.ext import commands, tasks

from .. import utils
from ..config import OWNER_ID
from ..utils import (Field, Log, db, mk_embed, normal_command, owner_command,
                     toKCT)


class Events(commands.Cog):
    def __init__(self, bot):
        # pylint: disable=no-member
        self.bot = bot
        self.twitch_drops_loop.start()
        self.db = db.TwitchDropsDB()
        self.db.connect()

    def cog_unload(self):
        self.db.close()

    @normal_command("드롭스")
    async def 드롭스(self, ctx):
        TITLE = "https://seaofthieves.gamepedia.com/Twitch_Drops"
        embedfields = []
        last = self.db.last

        for drop in last[1]:
            start = toKCT(drop.startdate)
            end = toKCT(drop.enddate)

            startstr = f"{start.month}월 {start.day}일 {start.hour}시"
            endstr = f"{end.month}월 {end.day}일 {end.hour}시"
            embedfields.append(
                Field(f"{drop.reward}", f"{startstr} ~ {endstr}", False))

        footer = "데이터는 정확하지 않을 수 있습니다."

        embed = mk_embed(last[0], *embedfields,
                         titleurl=TITLE, color=0x9246ff, footer=footer)
        await ctx.send(embed=embed)

    @owner_command
    async def dropsupdate(self, ctx):
        await self.get_twitch_drops(True)

    async def get_twitch_drops(self, forceupdate=False):
        DROPSURL = "https://seaofthieves.gamepedia.com/Twitch_Drops?action=raw"
        async with aiohttp.ClientSession() as session:
            async with session.get(DROPSURL) as res:
                if res.status != 200:
                    return

                text = await res.text()

                parsed = wikitextparser.parse(text)
                fsec = parsed.sections[1]
                title = fsec.title.strip()
                last = self.db.last
                if last is not None and title == last[0] and not forceupdate:
                    Log.v(v="드롭스 변경 없음")
                    return
                table = fsec.tables[0]
                td = table.data()

                filep = r"\[\[File:(?P<filename>.+)\|\d+px\]\]"
                linkp = r"\[\[(?P<name>.+)\]\]"
                filere = re.compile(filep)
                linkre = re.compile(linkp)

                dropslist = []

                for t in td[1:]:
                    # imagelink = "https://seaofthieves.gamepedia.com/File:{}"
                    reward = ""
                    for d in t:
                        fm = filere.match(d)
                        lm = linkre.match(d)

                        if fm is not None:
                            continue
                        elif lm is not None:
                            reward = []
                            for r in d.split("\n"):
                                lm = linkre.match(r)
                                reward.append(lm.group("name"))
                        else:
                            startdate = datetime.datetime.utcnow()
                            r = datetime.datetime.strptime(d, "%B %d")
                            startdate = startdate.replace(
                                month=r.month, day=r.day, hour=9, minute=0)
                            enddate = startdate + datetime.timedelta(days=1)

                    dropslist.append(
                        db.Drops(", ".join(reward), startdate, enddate))

        self.db.insert(title, dropslist)
        Log.v(v="드롭스 불러옴")

    @tasks.loop(hours=2)
    async def twitch_drops_loop(self, forceupdate=False):
        await self.get_twitch_drops()

    @twitch_drops_loop.error
    async def twitch_drops_error(self, error):
        Log.e(error=error)
        trace = utils.get_traceback(error)
        print(trace)
        await self.bot.get_user(OWNER_ID).send(f"드롭스 에러\n{trace}")

    @twitch_drops_loop.before_loop
    async def before_twitch_drops(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(Events(bot))
