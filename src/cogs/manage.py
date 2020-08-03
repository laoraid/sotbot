import re

from discord.ext import commands

from .. import utils
from ..utils import mkhelpstr


class Manage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['help'], description='이 도움말을 출력합니다.')
    async def 도움말(self, ctx, cmd):
        if cmd == 'help' or cmd == "도움말":
            await ctx.send(embed=utils.helpembed)
        elif cmd in utils.viscomsdict:
            await ctx.send(f"{utils.viscomsdict[cmd].help}")
        else:
            await ctx.send(f'``{cmd}`` 명령어를 찾을 수 없습니다.')

    @commands.command(description="xbox 아이디가 포함되게 닉네임을 변경합니다.",
                      help=mkhelpstr("아이디", "xboxid"))
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


def setup(bot):
    bot.add_cog(Manage(bot))
