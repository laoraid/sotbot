from discord.ext import commands

from .. import utils
from ..utils import cb


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
            await ctx.send(f'{cb(cmdname)} 명령어를 찾을 수 없습니다.')

    @commands.command(hidden=True)
    async def 테스트(self, ctx):
        await ctx.send("테스트 성공")


def setup(bot):
    bot.add_cog(Manage(bot))
