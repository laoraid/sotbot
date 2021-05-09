import re
from src.config import OWNER_ID

import discord
from discord.ext import commands, tasks

from ..utils import mkhelpstr, normal_command, Log
from .. import utils


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
                    await t[0].delete()
                Log.v(None, f"{c.name} 보이스채널 삭제")
                await c.delete()

        for guild in self.bot.guilds:
            voicechs = [
                x
                for x in guild.voice_channels
                if len(x.members) == 0 and re.match(r".+#\d$", x.name) is not None
            ]
            self.emptychset.update(voicechs)

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


def setup(bot):
    bot.add_cog(Server(bot))
