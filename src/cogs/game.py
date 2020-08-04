import re
import difflib
import datetime
import aiohttp

import discord
from discord.ext import commands
import openpyxl
from bs4 import BeautifulSoup

from ..utils import dt_to_str, mkhelpstr
from .. import utils

RELOAD_TIME = datetime.timedelta(minutes=3)


class Game(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.lastchktime = None
        self.lastserverstat = ""

        sheet = openpyxl.load_workbook(
            './islands.xlsx', data_only=True)['Sheet1']
        i = 2
        self.islandspos = {}
        self.engislandpos = {}
        while (True):
            islandname = sheet.cell(row=i, column=1).value

            if islandname is None:
                break
            pos = sheet.cell(row=i, column=2).value
            region = sheet.cell(row=i, column=3).value
            engname = sheet.cell(row=i, column=4).value

            v = [pos, region, engname]

            self.islandspos[islandname] = v
            self.engislandpos[engname] = v
            i += 1

    @commands.command(aliases=['pos'], description="섬의 좌표와 위키 링크를 출력합니다.",
                      help=mkhelpstr("좌표", "섬 이름"))
    async def 좌표(self, ctx, *, island):
        island = island.lower()

        iseng = re.match(r'[^ㄱ-ㅎㅏ-ㅣ가-힣]', island)
        iseng = True if iseng is not None else False

        if iseng:
            islands = list(self.engislandpos.keys())
        else:
            islands = list(self.islandspos.keys())

        substr = [x for x in islands if island in x.lower()]

        if (len(substr) == 0):
            clmat = difflib.get_close_matches(island, islands, cutoff=0.5)
            if (len(clmat) == 0):
                await ctx.send(f"``{island}`` 섬을 찾을 수 없습니다.")
                return None
            else:
                island = clmat[0]
        else:
            island = substr[0]
        await ctx.send(embed=self.make_pos_embed(island, iseng))

    def make_pos_embed(self, name, iseng):
        if iseng:
            pr = self.engislandpos[name]
        else:
            pr = self.islandspos[name]
        urlname = pr[2].replace(" ", "_")
        WIKI_URL = f"https://seaofthieves.gamepedia.com/{urlname}"
        embed = discord.Embed(title=name, url=WIKI_URL)
        embed.add_field(name="좌표", value=pr[0], inline=True)
        embed.add_field(name="해역", value=pr[1], inline=True)
        embed.set_footer(text="섬 이름 클릭시 위키로 이동됨")
        return embed

    @commands.command(description="서버 상태를 확인합니다. 쿨타임 3분",
                      help=mkhelpstr("서버"))
    async def 서버(self, ctx):
        STATURL = "https://www.seaofthieves.com/ko/status"
        SERVER_IS_SICK = ":regional_indicator_x: 점검중이거나 서버가 터졌어요."
        SERVER_HEALTHY = ":white_check_mark: 서버가 정상이에요."
        SERVER_UNKNOWN = "서버 상태를 확인할 수 없어요."

        msg = None

        if self.lastchktime is None:
            cachetime = RELOAD_TIME
        else:
            cachetime = datetime.datetime.utcnow() - self.lastchktime

        if not cachetime < RELOAD_TIME:
            msg = await ctx.send("서버 상태 확인중...")
            async with aiohttp.ClientSession() as session:
                async with session.get(STATURL) as res:
                    self.lastchktime = datetime.datetime.utcnow()
                    self.lastchktime = utils.toKCT(self.lastchktime)

                    if res.status == 200:
                        soup = BeautifulSoup(await res.text(), 'html.parser')
                    elif res.status != 200 or res is None:
                        self.lastserverstat = SERVER_UNKNOWN
                        await ctx.send(self.lastserverstat)
                        return None

            srvinfo = soup.find("div", {"class": "service__info"})
            text = srvinfo.find("h2").contents[0]

            if text == "문제가 발생하여 서비스에 지장이 있습니다.":
                self.lastserverstat = SERVER_IS_SICK
            if text == "모든 서비스가 정상 운영되고 있습니다.":
                self.lastserverstat = SERVER_HEALTHY
            else:
                self.lastserverstat = SERVER_UNKNOWN

        lctstr = dt_to_str(self.lastchktime)

        if msg is not None:
            await msg.delete()

        await ctx.send(f"{self.lastserverstat} 확인 시간 : ``{lctstr}``")


def setup(bot):
    bot.add_cog(Game(bot))
