import datetime

import aiohttp
import tossi
from bs4 import BeautifulSoup
from discord.ext import commands

from .. import utils
from ..classes.datafinder import IslandFinder
from ..utils import (BST, KCT, PST, Field, Log, UTCnow, cb, converters, fmdate,
                     hfmdate, mk_embed, normal_command, str_help_by_cmd, utcto)

RELOAD_TIME = datetime.timedelta(minutes=3)


def clr_region(region):
    RED = 0xd22b55
    GREEN = 0x05f445
    GRAY = 0x7c828e
    PURPLE = 0x620062

    if region == "The Devil's Roar":
        return RED
    if region == "The Shores of Plenty":
        return GREEN
    if region == "The Wilds":
        return GRAY
    if region == "The Ancient Isles":
        return PURPLE

    return utils.randcolor()


class Game(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.lastchktime = None
        self.lastserverstat = ""

        self.islandfinder = IslandFinder()

    def cog_unload(self):
        self.islandfinder.close()

    @normal_command("좌표", "섬 이름", aliases=["pos"])
    async def 좌표(self, ctx, *, island):
        origin = island
        island = island.lower()

        t = self.islandfinder.findisland(island)

        if t is None:
            await ctx.send(f"{cb(island)} 섬을 찾을 수 없습니다.")
            Log.v(ctx, f"{island} 검색 실패")
            return None

        if(t["useddiff"]):
            Log.v(ctx, f"{origin} --> {t['islandname']} 유사 문자열")
        else:
            Log.v(ctx, f"{origin} --> {t['islandname']} 부분 문자열")

        await ctx.send(embed=self.make_pos_embed(t))

    def make_pos_embed(self, t):
        embed = utils.mk_embed(t["islandname"],
                               Field("좌표", t["pos"]),
                               Field("동물", t["animal"]),
                               Field("해역", t["region"], False),
                               titleurl=t["wikiurl"],
                               color=clr_region(t["region"]),
                               footer="섬 이름 클릭시 위키로 이동됨")
        return embed

    @normal_command("서버", aliases=["server"])
    async def 서버(self, ctx):
        STATURL = "https://www.seaofthieves.com/ko/status"
        SERVER_IS_SICK = ":regional_indicator_x: 점검중이거나 서버가 터졌어요."
        SERVER_HEALTHY = ":white_check_mark: 서버가 정상이에요."
        SERVER_UNKNOWN = "서버 상태를 확인할 수 없어요."

        msg = None

        if self.lastchktime is None:
            cachetime = RELOAD_TIME
        else:
            utc = datetime.datetime.utcnow()
            utc = utils.UTC.localize(utc)
            cachetime = utc - self.lastchktime

        if not cachetime < RELOAD_TIME:
            msg = await ctx.send("서버 상태 확인중...")
            async with aiohttp.ClientSession() as session:
                async with session.get(STATURL) as res:
                    self.lastchktime = datetime.datetime.utcnow()
                    self.lastchktime = utils.toKCT(self.lastchktime)

                    if res.status == 200:
                        soup = BeautifulSoup(await res.text(), 'html.parser')
                    elif res.status != 200 or res is None:
                        Log.v(ctx, "서버 상태 확인 불가")
                        self.lastserverstat = SERVER_UNKNOWN
                        await ctx.send(self.lastserverstat)
                        return None

            Log.v(ctx, "서버 상태 불러옴")
            srvinfo = soup.find("div", {"class": "service__info"})
            text = srvinfo.find("h2").contents[0]

            if text == "문제가 발생하여 서비스에 지장이 있습니다.":
                self.lastserverstat = SERVER_IS_SICK
            if text == "모든 서비스가 정상 운영되고 있습니다.":
                self.lastserverstat = SERVER_HEALTHY
            else:
                self.lastserverstat = SERVER_UNKNOWN
        else:
            Log.v(ctx, f"이전 상태 불러옴 {cachetime}")
        lctstr = fmdate(self.lastchktime)

        if msg is not None:
            await msg.delete()

        await ctx.send((f"{self.lastserverstat} 확인 시간 : {cb(lctstr)} "
                        "실제 서버 상태와 다를 수 있어요."))

    @normal_command("동물", "현재 좌표", "동물1", "동물2...")
    async def 동물(self, ctx, p: converters.Position,
                 n: commands.Greedy[converters.Animal]):
        if len(n) == 0:
            raise commands.BadArgument(
                f"동물 이름을 알 수 없습니다. {str_help_by_cmd('동물')}")

        n = set(n)
        closeisland = self.islandfinder.close_island(p, n)

        if closeisland is None:
            await ctx.send(f"조건에 맞는 섬을 찾을 수 없습니다. {str_help_by_cmd('동물')}")
            Log.v(ctx, "조건에 맞는 섬 검색 실패")
            return None

        animalstrs = [converters.decode_animal(x) for x in n]
        animalstrs = f"{cb(', '.join(animalstrs))}"
        animalstrs = tossi.postfix(animalstrs, "이")

        await ctx.send(f"{cb(p)}에서 {animalstrs} 있는 가장 가까운 섬은...",
                       embed=self.make_pos_embed(closeisland))

    @normal_command("시간", aliases=["time", "시각"])
    async def 시간(self, ctx):
        embed = mk_embed("현재 시각은...",
                         Field("KCT", hfmdate(utcto(KCT)), False),
                         Field("UTC/GMT", hfmdate(UTCnow()), False),
                         Field("BST", hfmdate(utcto(BST)), False),
                         Field("PST", hfmdate(utcto(PST)), False),
                         color=5234869)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Game(bot))
