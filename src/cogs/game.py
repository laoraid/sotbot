import datetime

import tossi
from discord.ext import commands

from .. import utils
from ..classes.datafinder import IslandFinder
from ..utils import (BST, KCT, PST, Field, Log, UTCnow, cb, converters,
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
