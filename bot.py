import os
import difflib
import re
from discord.ext import commands
import discord
import pandas as pd

try:
    BOT_TOKEN = os.environ['BOT_TOKEN']
except KeyError:
    import config
    BOT_TOKEN = config.TOKEN

bot = commands.Bot(command_prefix='!')
islandspos = pd.read_excel('islands.xlsx',
                           header=0,
                           index_col=0).to_dict()['pos']


@bot.command()
async def 아이디(ctx: commands.Context, *args):
    if (len(args) == 0):
        await ctx.send('사용법 : ``!아이디`` ``xboxid``')
        return None
    prevnick = ctx.author.display_name
    id = args[0]

    pattern = r'(?P<nickname>\S+)\s*\(.+\)'

    mat = re.match(pattern, prevnick)

    if not mat is None:
        nick = f'{mat.group("nickname")}({id})'
    else:
        nick = f'{prevnick}({id})'

    await ctx.author.edit(nick=nick)
    await ctx.send(f'{prevnick}의 닉네임이 {nick}으로 변경되었습니다.')


@bot.command()
async def 좌표(ctx, *args):
    if (len(args) == 0):
        await ctx.send('사용법 : ``!좌표`` ``섬 이름``')
        return None

    args = [x.lower() for x in args]
    island = ' '.join(args)
    islands = list(islandspos.keys())

    clmat = difflib.get_close_matches(island, islands, cutoff=0.5)

    if (len(clmat) == 0):
        substr = [x for x in islands if island in x.lower()]
        if (len(substr) == 0):
            await ctx.send(f"``{island}`` 섬을 찾을 수 없습니다.")
            return None
        else:
            island = substr[0]
    else:
        island = clmat[0]
    await ctx.send(f"``{island}``의 좌표는 ``{islandspos[island]}``")


@bot.event
async def on_member_join(member):
    msg = (f'{member.mention} ``!아이디`` ``xboxid`` 로 게임 내 아이디 지정하고\n'
           '규칙은 https://discord.gg/QhHZJUH 보고 겜하셈')
    ch = bot.get_channel(726374943121473627)
    await ch.send(msg)

print('봇 실행중')
bot.run(BOT_TOKEN)
