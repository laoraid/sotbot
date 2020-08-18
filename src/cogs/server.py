import re
import asyncio

import discord
from discord.ext import commands, tasks
import tossi

from ..utils.converters import Ship
from ..config import CATEGORIES, OWNER_ID, ADD_CATEGORIES
from .. import utils
from ..utils import mkhelpstr, Log, cb


def _get_cats_by_guildID(guildid, add=False):
    if not add:
        return CATEGORIES[guildid]
    return ADD_CATEGORIES[guildid]


def _get_cat_by_ch(ch, shipidx, add=False):
    ct = _get_cats_by_guildID(ch.guild.id, add)
    return discord.utils.get(ch.guild.categories, id=ct[shipidx])


async def _make_ch(cat, name, pos):
    ch = await cat.create_voice_channel(name)
    await ch.edit(position=pos)
    return ch


def _regex_voicech(chname):
    p = r"(추가 )?(?P<name>\D+)\s-\s(?P<num>\d+)"
    return re.match(p, chname)


def _get_empty_num(cat):
    chnames = [x.name for x in cat.voice_channels]
    num = 1

    for name in chnames:
        m = _regex_voicech(name)
        if m.group("num") != str(num):
            return num
        num += 1

    return num


class Server(commands.Cog):
    def __init__(self, bot: commands.Bot):
        # pylint: disable=no-member
        self.bot = bot
        self.clearchannel.start()
        self.lock = asyncio.Lock()

    @tasks.loop(seconds=60)
    async def clearchannel(self):
        for guild in self.bot.guilds:
            cats = _get_cats_by_guildID(guild.id, add=True)
            for catid in cats:
                cat = discord.utils.get(guild.categories, id=catid)
                vcs = cat.voice_channels

                for vc in vcs:
                    if len(vc.members) == 0:
                        chname = vc.name
                        await vc.delete()
                        Log.v(None, f"{chname} 채널 삭제됨")

    @clearchannel.before_loop
    async def before_clearchannel(self):
        await self.bot.wait_until_ready()

    @clearchannel.error
    async def clearchannel_error(self, error):
        Log.e(error=error)
        trace = utils.get_traceback(error)
        print(trace)
        await self.bot.get_user(OWNER_ID).send(f"채널 청소 에러\n{trace}")

    @commands.command(description="배 종류 별로 보이스 채널을 만듭니다.",
                      usage=mkhelpstr("출항", "배 종류"))
    @commands.cooldown(1, 5, type=commands.BucketType.user)
    async def 출항(self, ctx, ship: Ship):
        author = ctx.message.author
        if author.voice is not None:  # check already in ship channel
            invoice = True
            chname = author.voice.channel.name
            m = _regex_voicech(chname)

            if m is not None:
                await ctx.send(f"{author.mention} 이미 채널에 있어요."
                               " 채널에서 나간 뒤 실행해주세요.")
                ctx.command.reset_cooldown(ctx)
                return None
        else:
            invoice = False

        origincat = _get_cat_by_ch(ctx.channel, ship["id"])
        cat = _get_cat_by_ch(ctx.channel, ship["id"], True)
        emptych = [x for x in origincat.voice_channels if len(x.members) == 0]
        emptych.extend([x for x in cat.voice_channels if len(x.members) == 0])

        if len(emptych):  # check empty channel
            emptychexist = True
            name = emptych[0].name

            ch = discord.utils.get(emptych, name=name)
            name = tossi.postfix(f"{cb(name)}", "이")
            await ctx.send(f"{author.mention} 이미 비어있는 방 {name} 있어요.")
            ctx.command.reset_cooldown(ctx)
        else:
            async with self.lock:
                num = _get_empty_num(cat)

                emptychexist = False
                name = f"추가 {ship['name']} - {num}"

                ch = await _make_ch(cat, name, num - 1)
                Log.v(ctx, f"채널 {name} 생성됨")
                name = tossi.postfix(f"{cb(name)}", "이")
                await ctx.send(f"채널 {name} 생성되었습니다.")

        if invoice:
            await author.move_to(ch)
        elif not emptychexist:
            name = tossi.postfix(name, "으로")
            await ctx.send(f"{author.mention} 대기방에 있는 상태로 명령어를 입력하지 않으면"
                           f" 채널 생성 즉시 채널이 사라질 수도 있어요."
                           f" {name} 입장하세요.")

    @commands.command(description="xbox 아이디가 포함되게 닉네임을 변경합니다.",
                      usage=mkhelpstr("아이디", "xboxid"))
    async def 아이디(self, ctx, *, id):
        prevnick = ctx.author.display_name

        pattern = r'(?P<nickname>\S+)\s*\(.+\)'

        mat = re.match(pattern, prevnick)

        if mat is not None:
            nick = f'{mat.group("nickname")}({id})'
        else:
            nick = f'{prevnick}({id})'

        await ctx.author.edit(nick=nick)
        await ctx.send(f'{prevnick}의 닉네임이 {nick}으로 변경되었습니다.')

    @commands.command(hidden=True, help=mkhelpstr("역할부여", "역할이름"))
    @commands.has_permissions(administrator=True)
    async def 역할부여(self, ctx: commands.Context, r):
        guild = ctx.message.guild
        members = ctx.message.guild.members
        role = discord.utils.get(guild.roles, name=r)
        admin = discord.utils.get(guild.roles, name="관리직")

        for member in members:
            if admin not in member.roles and not member.bot:
                await member.add_roles(role)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def 테스트2(self, ctx, arg):
        await ctx.send(f"{arg} / 테스트 성공!재시작")


def setup(bot):
    bot.add_cog(Server(bot))
