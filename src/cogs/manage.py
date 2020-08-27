import os
import sys

import discord
from discord.ext import commands

from .. import utils
from ..utils import cb, owner_command, normal_command
from ..config import EXTENSIONS, CMD_PREFIX

COG_PREFIX = "src.cogs."


def tocog(modulename):
    return f"{COG_PREFIX}{modulename}"


def update_before(activity):
    async def wrapper(cog, ctx):
        await ctx.bot.change_presence(activity=discord.Game(activity),
                                      status=discord.Status.dnd)
    return wrapper


async def update_after(cog, ctx):
    await ctx.bot.change_presence(activity=discord.Game(f'{CMD_PREFIX}help'))
    utils.make_help_embed(ctx.bot)


class Manage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @normal_command("도움말", aliases=["help"])
    async def 도움말(self, ctx, cmdname):
        if cmdname == "help" or cmdname == "도움말":
            await ctx.send(embed=utils.helpembed)
        elif cmdname in utils.viscomsdict:
            cmd = utils.viscomsdict[cmdname]
            await ctx.send(embed=utils.make_cmd_help_embed(cmd))
        else:
            await ctx.send(f'{cb(cmdname)} 명령어를 찾을 수 없습니다.')

    @owner_command
    @commands.before_invoke(update_before("봇 재시작"))
    async def update(self, ctx):
        for ext in EXTENSIONS:
            self.bot.unload_extension(ext)
        await ctx.send("모든 모듈 언로드됨")

        await self.bot.logout()
        os.execl(sys.executable, sys.executable, "-m", "src.main")

    @owner_command
    @commands.before_invoke(update_before("파일 교체"))
    @commands.after_invoke(update_after)
    async def load(self, ctx, *, m):
        self.bot.load_extension(tocog(m))
        await ctx.send(f"{tocog(m)} 로드됨")

    @owner_command
    @commands.before_invoke(update_before("파일 교체"))
    @commands.after_invoke(update_after)
    async def unload(self, ctx, *, m):
        self.bot.unload_extension(tocog(m))
        await ctx.send(f"{tocog(m)} 언로드됨")

    @owner_command
    @commands.before_invoke(update_before("파일 교체"))
    @commands.after_invoke(update_after)
    async def _reload(self, ctx, *, m):
        self.unload_load(tocog(m))
        await ctx.send(f"{tocog(m)} 리로드됨")

    @owner_command
    @commands.before_invoke(update_before("파일 교체"))
    @commands.after_invoke(update_after)
    async def reloadall(self, ctx):
        for ext in EXTENSIONS:
            self.unload_load(ext)
            await ctx.send(f"{ext} 리로드됨")

    @owner_command
    async def 길드(self, ctx):
        guilds = []
        for g in self.bot.guilds:
            guilds.append(g.name)
        guilds = ", ".join(guilds)

        await ctx.send(f"길드 : {guilds}")

    @owner_command
    async def helphidden(self, ctx):
        hiddencmd = [c.name for c in self.bot.commands if c.hidden]
        ", ".join(hiddencmd)
        await ctx.send(hiddencmd)

    def unload_load(self, m):
        self.bot.unload_extension(m)
        self.bot.load_extension(m)


def setup(bot):
    bot.add_cog(Manage(bot))
