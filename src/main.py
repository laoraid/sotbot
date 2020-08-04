# region imports
import os

from discord.ext import commands
import discord

from . import utils
# endregion

CMD_PREFIX = "!"

bot = commands.Bot(command_prefix=CMD_PREFIX)
bot.owner_id = 226700060308668420


@bot.event
async def on_message(msg):
    allowchannel = [635398034469158914, 738655532709183551]
    # test channel, gall discord channel
    if msg.channel.id not in allowchannel:
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
            await ctx.send(f"사용법 : {ctx.command.help}")
    elif isinstance(error, commands.CommandNotFound):
        cmd = ctx.message.content.split(' ')[0][1:]
        await ctx.send(f"``{cmd}`` 명령어는 없는 명령어입니다.")
    elif isinstance(error, commands.MissingRole):
        await ctx.send("권한이 부족합니다.")
    else:
        utils.log_e(ctx, error)
        owner = f"<@!{bot.owner_id}>"
        await ctx.send(f"에러가 발생했습니다. {owner}")

try:
    BOT_TOKEN = os.environ['BOT_TOKEN']
except KeyError:
    from . import config
    BOT_TOKEN = config.TOKEN

bot.remove_command('help')

for ext in utils.extensions:
    bot.load_extension(ext)

utils.initbot(bot)
bot.run(BOT_TOKEN)
