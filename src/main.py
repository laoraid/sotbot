# region imports
from discord.ext import commands
import discord

from . import utils
from .config import (CMD_PREFIX, EXTENSIONS, OWNER_ID,
                     ALLOWED_CHANNEL, BOT_TOKEN)

# endregion

if __name__ == "__main__":

    bot = commands.Bot(command_prefix=CMD_PREFIX)
    bot.owner_id = OWNER_ID

    @bot.event
    async def on_message(msg):
        if msg.channel.id not in ALLOWED_CHANNEL:
            return
        await bot.process_commands(msg)

    @bot.event
    async def on_ready():
        await bot.change_presence(
            activity=discord.Game(name=f'{CMD_PREFIX}help'))
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
            utils.log_e(ctx, error="없는 명령어")
            cmd = ctx.message.content.split(' ')[0][1:]
            await ctx.send(f"``{cmd}`` 명령어는 없는 명령어입니다. "
                           f"도움말 : ``{CMD_PREFIX}도움말``")
        elif isinstance(error, commands.MissingRole):
            utils.log_e(ctx, error="권한 부족")
            await ctx.send("권한이 부족합니다.")
        elif isinstance(error, commands.BadArgument):
            pass  # 명령어 개별 처리
        elif isinstance(error, commands.CommandOnCooldown):
            utils.log_e(ctx, error="커맨드 쿨다운 상태")
            await ctx.send(f"{ctx.message.author.mention} 명령어 쿨타임입니다."
                           f" {error.retry_after:0.1f}초 뒤에 사용하세요.")
        else:
            utils.log_e(ctx, error=error)
            owner = f"<@!{bot.owner_id}>"
            await ctx.send(f"에러가 발생했습니다. {owner}에게 문의하세요.")
            trace = utils.get_traceback(error)
            print(trace)
            await bot.get_user(OWNER_ID).send(
                f"{ctx.message.content}\n{trace}")

    bot.remove_command('help')

    for ext in EXTENSIONS:
        bot.load_extension(ext)

    utils.initbot(bot)
    bot.run(BOT_TOKEN)
