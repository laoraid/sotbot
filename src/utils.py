import datetime
import pytz

import discord

KCT = pytz.timezone("Asia/Seoul")
UTC = pytz.utc

CMD_PREFIX = "!"

extensions = ["src.cogs.game", "src.cogs.manage"]


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


def dt_to_str(date, inclue_timezone=False):
    tz = ""
    if inclue_timezone:
        tz = " %Z%z"
    return date.strftime(f"%Y-%m-%d %H:%M:%S{tz}")


helpembed = discord.Embed(title="명령어 리스트")
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
        helpembed.add_field(name=', '.join(arr), value=c.description)

    helpembed.set_footer(text=f"'{CMD_PREFIX}help 명령어' 입력시 개별 명령어 도움말 출력")


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
    time = toKCT(datetime.datetime.now())
    now = dt_to_str(time, True)
    print(f"[error/{now}] | {ctx.message.content} | {error}")

def log_v(ctx, v):
    time = toKCT(ctx.message.created_at)
    ca = dt_to_str(time, True)
    print(f"[Vervose/{ca}] {ctx.message.content} | {v}")