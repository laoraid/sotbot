# region imports
import os
import traceback

from discord.ext import commands
import discord

from . import utils
from .config import CMD_PREFIX, EXTENSIONS, OWNER_ID, ALLOW_CHANNEL

# endregion


bot = commands.Bot(command_prefix=CMD_PREFIX)
bot.owner_id = OWNER_ID


@bot.event
async def on_message(msg):
    if msg.channel.id not in ALLOW_CHANNEL:
        return
    await bot.process_commands(msg)


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name=f'{CMD_PREFIX}help'))
    print(f'봇 실행중 서버 : {len(bot.guilds)}개')


@bot.event
async def on_command_error(ctx, error):
    utils.log_i(ctx)
    if isinstance(error, commands.MissingRequiredArgument):
        if ctx.command.name == "도움말":
            await ctx.send(embed=utils.helpembed)
        else:
            await ctx.send(embed=utils.make_cmd_help_embed(ctx.command))
    elif isinstance(error, commands.CommandNotFound):
        utils.log_e(ctx, "없는 명령어")
        cmd = ctx.message.content.split(' ')[0][1:]
        await ctx.send(f"``{cmd}`` 명령어는 없는 명령어입니다.")
    elif isinstance(error, commands.MissingRole):
        utils.log_e(ctx, "권한 부족")
        await ctx.send("권한이 부족합니다.")
    elif isinstance(error, commands.BadArgument):
        pass  # 명령어 개별 처리
    else:
        utils.log_e(ctx, error)
        owner = f"<@!{bot.owner_id}>"
        await ctx.send(f"에러가 발생했습니다. {owner}에게 문의하세요.")
        trace = traceback.format_exception(
            type(error), error, error.__traceback__)
        trace = "".join(trace)
        print(trace)
        await bot.get_user(OWNER_ID).send(f"{ctx.message.content}\n{trace}")


try:
    BOT_TOKEN = os.environ['BOT_TOKEN']
except KeyError:
    from . import bottoken
    BOT_TOKEN = bottoken.TOKEN

bot.remove_command('help')

for ext in EXTENSIONS:
    bot.load_extension(ext)

utils.initbot(bot)
bot.run(BOT_TOKEN)
