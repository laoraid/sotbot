import re
import difflib
import datetime
import aiohttp
import math

from discord.ext import commands
from bs4 import BeautifulSoup
import tossi

from .. import utils
from ..utils import dt_to_str, cb, Field, normal_command
from ..utils import db, converters, Log
from ..utils.converters import convert_animal
from ..config import CMD_PREFIX

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

        self.db = db.IslandDB()
        self.db.connect()

    def cog_unload(self):
        self.db.close()

    @normal_command("좌표", "섬 이름", aliases=["pos"])
    async def 좌표(self, ctx, *, island):
        origin = island
        island = island.lower()

        iseng = re.match(r'[^ㄱ-ㅎㅏ-ㅣ가-힣]', island)
        iseng = True if iseng is not None else False

        if iseng:
            islands = self.db.field("Engname")
        else:
            islands = self.db.field("KRname")

        substr = [x for x in islands if re.search(rf"\b{island}\b", x.lower())]
        if len(substr) == 0:
            substr = [x for x in islands if island in x.lower()]

        if len(substr) == 0:
            clmat = difflib.get_close_matches(island, islands, cutoff=0.3)
            if len(clmat) == 0:
                await ctx.send(f"{cb(island)} 섬을 찾을 수 없습니다.")
                Log.v(ctx, f"{island} 검색 실패")
                return None
            else:
                island = clmat[0]
                ratio = difflib.SequenceMatcher(None, origin, island).ratio()
                Log.v(ctx, f"{origin} -> {island} (유사도 : {ratio:.2f})")
        else:
            island = substr[0]
            Log.v(ctx, f"{origin} -> {island} (부분 문자열)")
        await ctx.send(embed=self.make_pos_embed(island, iseng))

    def make_pos_embed(self, name, iseng):
        if iseng:
            data = self.db.get_data_by_name("eng", name)
        else:
            data = self.db.get_data_by_name("kr", name)
        urlname = data["engname"].replace(" ", "_")
        WIKI_URL = f"https://seaofthieves.gamepedia.com/{urlname}"
        embed = utils.mk_embed(name,
                               Field("좌표", data["pos"]),
                               Field("동물", value=convert_animal(data)),
                               Field("해역", data["region"], False),
                               titleurl=WIKI_URL, color=clr_region(
                                   data["region"]),
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
        lctstr = dt_to_str(self.lastchktime)

        if msg is not None:
            await msg.delete()

        await ctx.send(f"{self.lastserverstat} 확인 시간 : {cb(lctstr)}")

    def _close_island(self, pos, animals):
        def get_int(pos):
            x = ord(pos[0])
            y = int(pos[1:])
            return (x, y)

        def get_distance(x1, y1, x2, y2):
            dx = (x1 - x2) ** 2
            dy = (y1 - y2) ** 2

            return math.sqrt(dx + dy)

        stx, sty = get_int(pos)
        islands = self.db.get_data_by_animal(animals)

        if len(islands) == 0:
            return None

        distemp = 9999
        islandtemp = ""

        for island in islands:
            isx, isy = get_int(island["pos"].replace("-", ""))
            dis = get_distance(stx, sty, isx, isy)
            if distemp > dis:
                distemp = dis
                islandtemp = island["krname"]

        return islandtemp

    @normal_command("동물", "현재 좌표", "동물1", "동물2...")
    async def 동물(self, ctx, p: converters.Position,
                 n: commands.Greedy[converters.Animal]):
        if len(n) == 0:
            raise commands.BadArgument(
                f"동물 이름을 알 수 없습니다.\nEX) {CMD_PREFIX}동물 E21 닭 돼지")

        n = set(n)
        closeisland = self._close_island(p, n)

        if closeisland is None:
            await ctx.send("조건에 맞는 섬을 찾을 수 없습니다.")
            Log.v(ctx, "조건에 맞는 섬 검색 실패")
            return None

        animalstrs = [converters.decode_animal(x) for x in n]
        animalstrs = f"{cb(', '.join(animalstrs))}"
        animalstrs = tossi.postfix(animalstrs, "이")

        await ctx.send(f"{cb(p)}에서 {animalstrs} 있는 가장 가까운 섬은...",
                       embed=self.make_pos_embed(closeisland, False))


def setup(bot):
    bot.add_cog(Game(bot))
