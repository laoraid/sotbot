import re
import asyncio

import discord
from discord.ext import commands, tasks
import tossi

from ..utils.converters import Ship
from ..config import (ALLOWED_CHANNEL, CATEGORIES, OWNER_ID,
                      ADD_CATEGORIES)
from .. import utils
from ..utils import mkhelpstr


class Server(commands.Cog):
    def __init__(self, bot: commands.Bot):
        # pylint: disable=no-member
        self.bot = bot
        self.clearchannel.start()
        self.lock = asyncio.Lock()

    def _cats_by_ch(self, ch, add=False):
        if ch.id in ALLOWED_CHANNEL:
            if not add:
                idx = ALLOWED_CHANNEL.index(ch.id)
                return CATEGORIES[idx]
            else:
                idx = ALLOWED_CHANNEL.index(ch.id)
                return ADD_CATEGORIES[idx]
        else:
            raise ValueError

    def _get_cat_by_ch(self, ch, ship, add=False):
        catsid = self._cats_by_ch(ch, add)[ship]
        return discord.utils.get(ch.guild.categories, id=catsid)

    async def _make_ch(self, cat, name, pos):
        ch = await cat.create_voice_channel(name)
        await ch.edit(position=pos)
        return ch

    def _regex_voicech(self, chname):
        p = r"[추가 ]?(?P<name>\D+)\s-\s(?P<num>\d+)"
        return re.match(p, chname)

    def _get_empty_num(self, cat):
        chnames = [x.name for x in cat.voice_channels]

        num = 1

        for name in chnames:
            m = self._regex_voicech(name)
            if m.group("num") != str(num):
                return num
            num += 1

        return num

    @tasks.loop(seconds=60)
    async def clearchannel(self):
        guild = self.bot.guilds[0]
        for catid in ADD_CATEGORIES:
            cat = discord.utils.get(guild.categories, id=catid)
            if cat is None:
                continue
            vcs = cat.voice_channels

            for vc in vcs:
                if len(vc.members) == 0:
                    chname = vc.name
                    await vc.delete()
                    utils.log_v(None, f"{chname} 채널 삭제됨")

    @clearchannel.before_loop
    async def before_clearchannel(self):
        await self.bot.wait_until_ready()

    @clearchannel.error
    async def clearchannel_error(self, error):
        utils.log_e(error=error)
        trace = utils.get_traceback(error)
        print(trace)
        await self.bot.get_user(OWNER_ID).send(f"채널 청소 에러\n{trace}")

    @commands.command(description="배 종류 별로 보이스 채널을 만듭니다.",
                      usage=mkhelpstr("출항", "배 종류"))
    @commands.cooldown(1, 5, type=commands.BucketType.user)
    async def 출항(self, ctx, ship: Ship):
        author = ctx.message.author
        if author.voice is not None:
            voice = True
            chname = author.voice.channel.name
            m = self._regex_voicech(chname)

            if m is not None:
                await ctx.send(f"{author.mention} 이미 채널에 있어요."
                               " 채널에서 나간 뒤 실행해주세요.")
                ctx.command.reset_cooldown(ctx)
                return None
        else:
            voice = False

        origincat = self._get_cat_by_ch(ctx.channel, ship["id"])
        cat = self._get_cat_by_ch(ctx.channel, ship["id"], True)
        emptych = [x for x in origincat.voice_channels if len(x.members) == 0]
        emptych.extend([x for x in cat.voice_channels if len(x.members) == 0])

        if len(emptych):
            emptychexist = True
            name = emptych[0].name
            name = tossi.postfix(name, "이")

            ch = discord.utils.get(emptych, name=name)
            await ctx.send(f"{author.mention} 이미 비어있는 방 {name} 있어요.")
            ctx.command.reset_cooldown(ctx)
        else:
            async with self.lock:
                num = self._get_empty_num(cat)

                emptychexist = False
                name = f"추가 {ship['name']} - {num}"

                ch = await self._make_ch(cat, name, num - 1)
                utils.log_v(ctx, f"채널 {name} 생성됨")

        if voice:
            await author.move_to(ch)
        elif not emptychexist:
            pick = tossi.pick(name, "으로")
            await ctx.send(f"{author.mention} 대기방에 있는 상태로 명령어를 입력하지 않으면"
                           f" 채널 생성 즉시 채널이 사라질 수도 있어요."
                           f" ``{name}``{pick} 입장하세요.")


def setup(bot):
    bot.add_cog(Server(bot))
