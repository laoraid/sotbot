import re

from src.config import OWNER_ID

import discord
from discord.ext import commands, tasks

from ..utils import mkhelpstr, normal_command, Log, owner_command
from .. import utils


def find_missing(arr):
    for i in range(len(arr) - 1):
        if arr[i] + 1 != arr[i + 1]:
            return arr[i] + 1
    return arr[-1] + 1


class Server(commands.Cog):
    def __init__(self, bot: commands.Bot):
        # pylint: disable=no-member
        self.bot = bot
        self.clearchannel.start()
        self.emptychset = set()

    @tasks.loop(seconds=20)
    async def clearchannel(self):
        while self.emptychset:
            c = self.emptychset.pop()
            if c in c.guild.voice_channels and len(c.members) == 0:
                txtchs = [x for x in c.guild.text_channels]
                t = [x for x in txtchs if x.name == c.name.replace("#", "")]
                if len(t) > 0:
                    Log.v(None, f"{t[0].name} 텍스트채널 삭제")
                    try:
                        await t[0].delete()
                    except discord.errors.Forbidden:
                        pass
                    except discord.errors.NotFound:
                        pass
                Log.v(None, f"{c.name} 보이스채널 삭제")
                try:
                    await c.delete()
                except discord.errors.Forbidden:
                    pass
                except discord.errors.NotFound:
                    pass

        for guild in self.bot.guilds:
            voicechs = [
                x
                for x in guild.voice_channels
                if len(x.members) == 0 and (re.match(r".+#\d+$", x.name) is not None)
            ]
            self.emptychset.update(voicechs)

    @owner_command
    async def stop_clear(self, ctx):
        self.clearchannel.stop()


    @clearchannel.before_loop
    async def before_clearchannel(self):
        await self.bot.wait_until_ready()

    @clearchannel.error
    async def clearchannel_error(self, error):
        Log.e(error=error)
        trace = utils.get_traceback(error)
        print(trace)
        await self.bot.get_user(OWNER_ID).send(f"채널 청소 에러\n\n{trace}")

    @normal_command("아이디", "xboxid")
    async def 아이디(self, ctx, *, id):
        prevnick = ctx.author.display_name

        pattern = r"(?P<nickname>\S+)\s*\(.+\)"

        mat = re.match(pattern, prevnick)

        if mat is not None:
            nick = f'{mat.group("nickname")}({id})'
        else:
            nick = f"{prevnick}({id})"

        if len(nick) > 32:
            await ctx.send(f"{ctx.author.mention} 닉네임이 너무 깁니다.")
            return

        await ctx.author.edit(nick=nick)
        await ctx.send(f"{prevnick}의 닉네임이 {nick}으로 변경되었습니다.")

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

    @normal_command("출항")
    @commands.cooldown(100, 10, commands.BucketType.user)
    async def 출항(self, ctx: commands.Context):
        vc = ctx.author.voice
        if vc is not None and "띄우기" in vc.channel.name:
            name = vc.channel.name.replace("띄우기", "").strip()
            category = vc.channel.category
            findnum = [
                int(x.name.split("#")[1])
                for x in category.voice_channels
                if "#" in x.name and name in x.name
            ]

            findnum.append(0)
            findnum.sort()

            name += f"#{find_missing(findnum)}"
            ch = await category.create_voice_channel(name)
            Log.v(ctx, f"보이스 채널 생성 {name}")

            await ctx.author.move_to(ch)
        else:
            await ctx.send(f"{ctx.author.mention}, 띄우기 채널에 있을때만 동작합니다.")
            ctx.command.reset_cooldown(ctx)


def setup(bot):
    bot.add_cog(Server(bot))
