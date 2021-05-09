import re

import discord
from discord.ext import commands

from ..utils import mkhelpstr, normal_command


class Server(commands.Cog):
    def __init__(self, bot: commands.Bot):
        # pylint: disable=no-member
        self.bot = bot

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


def setup(bot):
    bot.add_cog(Server(bot))
