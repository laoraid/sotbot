import datetime
import pytz
from functools import wraps
import random

import discord
from discord.ext import commands

from ..config import CMD_PREFIX, LONG_DESCRIPTIONS

KCT = pytz.timezone("Asia/Seoul")
UTC = pytz.utc


def toKCT(date):
    if date.tzinfo is None:
        date = UTC.localize(date)
    return date.astimezone(KCT)


def mkhelpstr(cmd, *args):
    if len(args) != 0:
        args = "`` ``".join(args)
        args = f" ``{args}``"
    else:
        args = ""
    return f"``{CMD_PREFIX}{cmd}``{args}"


def dt_to_str(date, include_timezone=False):
    tz = ""
    if include_timezone:
        tz = " %Z%z"
    return date.strftime(f"%Y-%m-%d %H:%M:%S{tz}")


def randcolor():
    return random.randint(0, 16581375)


helpembed = discord.Embed(title="명령어 리스트", color=0x2ba3ee)
viscomsdict = {}
viscoms = []


def make_help_embed(bot):
    global viscomsdict, viscoms
    viscomsdict = {k: v for k,
                   v in bot.all_commands.items() if not v.hidden}
    viscoms = [x for x in bot.commands if not x.hidden]
    for c in viscoms:
        arr = [c.name]
        arr.extend(c.aliases)
        helpembed.add_field(name=', '.join(
            arr), value=c.description, inline=False)

    helpembed.set_footer(text=f"'{CMD_PREFIX}help 명령어' 입력시 개별 명령어 도움말 출력")


def memoize(pro=None):
    def inner(func):
        cache = {}

        @wraps(func)
        def ininner(arg):
            if pro is None:
                p = arg
            else:
                p = getattr(arg, pro)
            if p not in cache:
                cache[p] = func(arg)
            return cache[p]

        return ininner

    return inner


@memoize("name")
def make_cmd_help_embed(cmd: commands.Command):
    embed = discord.Embed(title=f"{cmd.name} 명령어", color=0xeec42b)

    embed.add_field(name="설명", value=LONG_DESCRIPTIONS[cmd.name], inline=False)
    embed.add_field(name="사용법", value=cmd.usage)

    return embed


def initbot(bot):
    @bot.before_invoke
    async def inner(ctx):
        log_i(ctx)
    make_help_embed(bot)
    return inner


def log_i(ctx):
    time = toKCT(ctx.message.created_at)
    ca = dt_to_str(time, True)
    print(f"[info/{ca}] {ctx.author} | {ctx.message.content}")


def log_e(ctx, error):
    time = toKCT(datetime.datetime.utcnow())
    now = dt_to_str(time, True)
    print(f"[error/{now}] | {ctx.message.content} | {error}")


def log_v(ctx=None, v=None):
    if ctx is None:
        time = toKCT(datetime.datetime.utcnow())
        content = ""
    else:
        time = toKCT(ctx.message.created_at)
        content = ctx.message.content

    ca = dt_to_str(time, True)

    print(f"[Verbose/{ca}] {content} | {v}")
