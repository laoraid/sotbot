import re

import discord
from discord.ext import commands

from .. import utils
from ..utils import mkhelpstr
from ..config import ALLOWED_CHANNEL


class Manage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['help'], description='이 도움말을 출력합니다.')
    async def 도움말(self, ctx, cmdname):
        if cmdname == 'help' or cmdname == "도움말":
            await ctx.send(embed=utils.helpembed)
        elif cmdname in utils.viscomsdict:
            cmd = utils.viscomsdict[cmdname]
            await ctx.send(embed=utils.make_cmd_help_embed(cmd))
        else:
            await ctx.send(f'``{cmdname}`` 명령어를 찾을 수 없습니다.')

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
    @commands.has_permissions(administrator=True)
    async def 봇말하기(self, ctx, t, title, value):
        embed = discord.Embed(title=title, color=utils.randcolor())
        embed.add_field(name="내용", value=value)

        if t == "갤":
            ch = ALLOWED_CHANNEL[1]
        else:
            ch = ALLOWED_CHANNEL[0]
        await self.bot.get_channel(ch).send(embed=embed)


def setup(bot):
    bot.add_cog(Manage(bot))
