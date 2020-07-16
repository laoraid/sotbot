import os
from discord.ext import commands
import discord

try:
    BOT_TOKEN = os.environ['BOT_TOKEN']
except KeyError:
    import config
    BOT_TOKEN = config.TOKEN

bot = commands.Bot(command_prefix='!')

@bot.command()
async def 아이디(ctx:commands.Context, *args):
    if (len(args) == 0):
        await ctx.send('사용법 : ``!아이디`` ``xboxid``')
        return None
    prevnick = ctx.author.display_name
    id = args[0]
    nick = prevnick + '(' + id + ')'
    await ctx.author.edit(nick=nick)
    await ctx.send(f'{prevnick}의 닉네임이 {nick}으로 변경되었습니다.')
    
@bot.event
async def on_member_join(member):
    msg = (f'{member.mention} 디시인사이드 Sea of Theives 갤러리 디스코드에 오신 걸 환영합니다.\n'
    '!아이디 ``xboxid`` 명령어로 게임 내 아이디를 지정해 주세요.\n'
    '규칙은 https://discord.gg/QhHZJUH 에서 확인 가능합니다.')
    ch = bot.get_channel(635398034469158914)
    await ch.send(msg)

    
bot.run(BOT_TOKEN)