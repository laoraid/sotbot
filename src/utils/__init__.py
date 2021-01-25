import random
import traceback
from datetime import datetime

import discord
import pytz
from discord.ext import commands

from ..config import CMD_PREFIX, LONG_DESCRIPTIONS

KCT = pytz.timezone("Asia/Seoul")
UTC = pytz.utc
BST = pytz.timezone("Europe/London")
PST = pytz.timezone("America/Los_Angeles")


def toKCT(date):
    if date.tzinfo is None:
        date = UTC.localize(date)
    elif date.tzinfo == KCT:
        return date
    return date.astimezone(KCT)


def utcto(timezone):
    return UTCnow().astimezone(timezone)


def UTCnow():
    return UTC.localize(datetime.utcnow())


def owner_command(func):
    return commands.command(hidden=True)(commands.is_owner()(func))


def normal_command(name, *args, aliases=None):
    des = short_des(name)
    usage = mkhelpstr(name, *args, aliases=aliases)
    if aliases is not None:
        cmd = commands.command(name, aliases=aliases,
                               description=des, usage=usage)
    else:
        cmd = commands.command(name, description=des, usage=usage)

    def inner(func):
        return cmd(func)
    return inner


def short_des(cmd):
    if isinstance(cmd, commands.Command):
        cmd = cmd.name
    ldes = LONG_DESCRIPTIONS[cmd]
    return ldes.split("\n")[0]


def mkEmptyList(buffer):
    return [None] * buffer


def mkhelpstr(cmd, *args, aliases=None):
    if aliases is None:
        aliases = [cmd]
    else:
        aliases = [cmd] + aliases
    helpstr = mkEmptyList(len(aliases))

    if len(args) != 0:
        args = "` `".join(args)
        args = f" `{args}`"
    else:
        args = ""

    for i, name in enumerate(aliases):
        helpstr[i] = f"`{CMD_PREFIX}{name}`{args}"

    return " 또는 ".join(helpstr)


def fmdate(date, include_timezone=False):
    tz = ""
    if include_timezone:
        tz = " %Z%z"
    return date.strftime(f"%Y-%m-%d %H:%M:%S{tz}")


def hfmdate(date, include_timezone=False):
    days = ["일", "월", "화", "수", "목", "금", "토"]
    tz = ""
    if include_timezone:
        tz = " %Z%z"
    day = date.strftime("%w")
    format = f"%Y년 %m월 %d일 {days[int(day)]}요일 %H시 %M분 %S초{tz}"
    format = format.encode("unicode-escape").decode()

    dstr = date.strftime(format).encode().decode("unicode-escape")
    return dstr


def randcolor():
    return random.randint(0, 16581375)


helpembed = discord.Embed(title="명령어 리스트", color=0x2ba3ee)
viscomsdict = {}
viscoms = []


def str_help_by_cmd(cmdname):
    return f"도움말 : `{CMD_PREFIX}help` `{cmdname}`"


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
