import os
import shutil

import discord
from discord.ext import commands

from .. import utils
from ..utils import cb
from ..config import EXTENSIONS, CMD_PREFIX


def update_before(activity):
    async def wrapper(cog, ctx):
        await ctx.bot.change_presence(activity=discord.Game(activity),
                                      status=discord.Status.dnd)
    return wrapper


async def update_after(cog, ctx):
    await ctx.bot.change_presence(activity=discord.Game(f'{CMD_PREFIX}help'))


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

    async def change_bot_presence(self, activity, status):
        await self.bot.change_presence(activity=discord.Game(activity),
                                       status=status)

    @commands.command(hidden=True)
    @commands.is_owner()
    @commands.before_invoke(update_before("파일 교체"))
    async def update(self, ctx):
        os.system("sudo shutdown -r now")

    @commands.command(hidden=True)
    @commands.is_owner()
    @commands.before_invoke(update_before("파일 교체"))
    @commands.after_invoke(update_after)
    async def load(self, ctx, *, m):
        self.bot.load_extension(m)

    @commands.command(hidden=True)
    @commands.is_owner()
    @commands.before_invoke(update_before("파일 교체"))
    @commands.after_invoke(update_after)
    async def unload(self, ctx, *, m):
        self.bot.unload_extension(m)

    @commands.command(name="reload", hidden=True)
    @commands.is_owner()
    @commands.before_invoke(update_before("파일 교체"))
    @commands.after_invoke(update_after)
    async def _reload(self, ctx, *, m):
        self.replace_reload(m)

    @commands.command(hidden=True)
    @commands.is_owner()
    @commands.before_invoke(update_before("파일 교체"))
    @commands.after_invoke(update_after)
    async def reloadall(self, ctx):
        for ext in EXTENSIONS:
            self.replace_reload(ext)

    def replace_reload(self, m):
        self.bot.unload_extension(m)
        filepath = f"{m.replace('.', '/')}.py"
        filename = os.path.basename(filepath)
        change_file(filename, filepath)
        self.bot.load_extension(m)


def change_file(filename, filepath):
    srcdir = os.environ["BOT_GIT_PATH"]
    srcdir = os.path.expanduser(srcdir)
    srcfile = os.path.join(srcdir, filepath)
    shutil.copy(srcfile, filepath)


def setup(bot):
    bot.add_cog(Manage(bot))
