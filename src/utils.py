import datetime

import discord

CMD_PREFIX = "!"

extensions = ["src.cogs.game", "src.cogs.manage"]


def mkhelpstr(cmd, *args):
    if len(args) != 0:
        args = "`` ``".join(args)
        args = f" ``{args}``"
    else:
        args = ""
    return f"``{CMD_PREFIX}{cmd}``{args}"


def dt_to_str(date):
    return date.strftime("%Y-%m-%d %H:%M:%S")


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
    ca = dt_to_str(ctx.message.created_at)
    print(f"[info/{ca}] {ctx.author} | {ctx.message.content}")


def log_e(ctx, error):
    now = dt_to_str(datetime.datetime.now())
    print(f"[error/{now}] | {ctx.message.content} | {error}")
