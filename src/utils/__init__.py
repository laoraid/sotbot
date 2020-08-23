import pytz
from functools import wraps
import random
import traceback

import discord
from discord.ext import commands

from ..config import CMD_PREFIX, LONG_DESCRIPTIONS

KCT = pytz.timezone("Asia/Seoul")
UTC = pytz.utc


def toKCT(date):
    if date.tzinfo is None:
        date = UTC.localize(date)
    return date.astimezone(KCT)


def mkEmptyList(buffer):
    return [None] * buffer


def mkhelpstr(cmd, *args, aliases=None):
    if aliases is None:
        aliases = [cmd]
    else:
        aliases = [cmd] + aliases
    helpstr = mkEmptyList(len(aliases))

    if len(args) != 0:
        args = "`` ``".join(args)
        args = f" ``{args}``"
    else:
        args = ""

    for i, name in enumerate(aliases):
        helpstr[i] = f"``{CMD_PREFIX}{name}``{args}"

    return " 또는 ".join(helpstr)


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
    return mk_embed(f"{cmd.name} 명령어",
                    Field("설명", LONG_DESCRIPTIONS[cmd.name], False),
                    Field("사용법", cmd.usage), color=0xeec42b)


def initbot(bot):
    make_help_embed(bot)


def get_traceback(error):
    trace = traceback.format_exception(
        type(error), error, error.__traceback__)
    trace = "".join(trace)
    return trace


def cb(string):
    return f"`{string}`"


class Field(object):
    def __init__(self, name, value, inline=True):
        self.name = name
        self.value = value
        self.inline = inline


def mk_embed(title, *fields, titleurl=None, color=None, footer=None):
    if color is None:
        color = randcolor()

    if titleurl is not None:
        embed = discord.Embed(title=title, url=titleurl, color=color)
    else:
        embed = discord.Embed(title=title, color=color)

    for f in fields:
        embed.add_field(name=f.name, value=f.value, inline=f.inline)

    if footer is not None:
        embed.set_footer(text=footer)

    return embed
