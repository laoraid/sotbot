import asyncio
import re

import discord
import tossi
from discord.ext import commands
from src.classes.datafinder import AfkMemory

from .. import utils
from ..config import ADD_CATEGORIES, CATEGORIES, CMD_PREFIX, OWNER_ID
from ..utils import Log, cb, mkhelpstr, normal_command, owner_command
from ..utils.converters import Ship


def _get_cats_by_guildID(guildid, add=False):
    if guildid not in CATEGORIES:
        return None
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
        # self.clearchannel.start()
        self.lock = asyncio.Lock()
        self._afkmem = AfkMemory()

    def cog_unload(self):
        self._afkmem.close()

    # @tasks.loop(seconds=60)
    async def clearchannel(self):
        for guild in self.bot.guilds:
            cats = _get_cats_by_guildID(guild.id, add=True)

            if cats is None:
                Log.e(error=f"알 수 없는 길드 아이디 : {guild.id}")
                return

            for catid in cats:
                cat = discord.utils.get(guild.categories, id=catid)
                vcs = cat.voice_channels

                for vc in vcs:
                    if len(vc.members) == 0:
                        chname = vc.name
                        await vc.delete()
                        Log.v(None, f"{chname} 채널 삭제됨")

    # @clearchannel.before_loop
    async def before_clearchannel(self):
        await self.bot.wait_until_ready()

    # @clearchannel.error
    async def clearchannel_error(self, error):
        Log.e(error=error)
        trace = utils.get_traceback(error)
        print(trace)
        await self.bot.get_user(OWNER_ID).send(f"채널 청소 에러\n{trace}")

    # @normal_command("출항", "배 종류")
    # @commands.cooldown(1, 5, type=commands.BucketType.user)
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

    @normal_command("아이디", "xboxid")
    async def 아이디(self, ctx, *, id):
        prevnick = ctx.author.display_name

        pattern = r'(?P<nickname>\S+)\s*\(.+\)'

        mat = re.match(pattern, prevnick)

        if mat is not None:
            nick = f'{mat.group("nickname")}({id})'
        else:
            nick = f'{prevnick}({id})'

        if len(nick) > 32:
            await ctx.send(f"{ctx.author.mention} 닉네임이 너무 깁니다.")
            return

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

    # @normal_command("잠수")
    async def 잠수(self, ctx: commands.Context):
        author = ctx.message.author
        id = author.id
        if id in self._afkmem:
            prevnick = self._afkmem[id]
            self._afkmem.pop(id)
            await author.edit(nick=prevnick, reason="잠수 명령어 해제")
            await ctx.send(f"{author.mention}, 잠수 상태가 해제되었습니다.")
        else:
            prevnick = author.nick
            await author.edit(nick="잠깐잠수중", reason="잠수 명령어 사용")
            await ctx.send(f"{author.mention}, 닉네임이 `잠깐잠수중` 으로 변경되었습니다.\n"
                           f"잠수 상태를 해제하려면 다시 {CMD_PREFIX}잠수 명령어를 사용하세요.")
            self._afkmem[id] = prevnick

    # @normal_command("모집", aliases=["recruit"])
    @owner_command
    async def 모집(self, ctx, *, what):
        author = ctx.message.author
        if author.voice is None:
            await ctx.send(f"{author.mention}, 보이스 채널에 들어간 뒤 실행해 주세요.")
            ctx.command.reset_cooldown(ctx)
            return None

        chname = author.voice.channel.name

        title = f"{chname} {what}"
        msg = await ctx.send(f"{author.mention}, 다음과 같이 글이 써집니다. "
                             f"제목 및 내용 : {title}\n"
                             "확인하셨으면 :thumbsup:, 취소하려면 :thumbsdown: 클릭")
        await msg.add_reaction("👍")
        await msg.add_reaction("👎")

        def check(reaction, user):
            if reaction.emoji in ("👍", "👎") and user == author:
                return True
            else:
                return False

        async def cancel():
            await ctx.send(f"{author.mention}, 취소되었습니다.")
            ctx.command.reset_cooldown(ctx)

        try:
            reaction, _ = await self.bot.wait_for("reaction_add",
                                                  timeout=60.0, check=check)
        except asyncio.TimeoutError:
            await cancel()
            return None
        else:
            if reaction.emoji == "👎":
                await cancel()
                return None

            await msg.delete()


def setup(bot):
    bot.add_cog(Server(bot))
