import os
import difflib
import re
import time

from discord.ext import commands
import discord

import openpyxl

import requests
# from bs4 import BeautifulSoup

try:
    BOT_TOKEN = os.environ['BOT_TOKEN']
except KeyError:
    import config
    BOT_TOKEN = config.TOKEN

bot = commands.Bot(command_prefix='!')
sheet = openpyxl.load_workbook('./islands.xlsx')['Sheet1']
i = 2
islandspos = {}
while (True):
    islandname = sheet.cell(row=i, column=1).value

    if islandname is None:
        break
    pos = sheet.cell(row=i, column=2).value
    region = sheet.cell(row=i, column=3).value

    islandspos[islandname] = [pos, region]
    i += 1


@bot.command()
async def 아이디(ctx: commands.Context, *args):
    if (len(args) == 0):
        await ctx.send('사용법 : ``!아이디`` ``xboxid``')
        return None
    prevnick = ctx.author.display_name
    id = args[0]

    pattern = r'(?P<nickname>\S+)\s*\(.+\)'

    mat = re.match(pattern, prevnick)

    if mat is not None:
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
    await ctx.send(embed=make_pos_embed(island))


def make_pos_embed(name):
    urlname = name.replace(" ", "_")
    WIKI_URL = f"https://seaofthieves.gamepedia.com/{urlname}"
    embed = discord.Embed(title=name, url=WIKI_URL)
    pr = islandspos[name]
    embed.add_field(name="좌표", value=pr[0], inline=True)
    embed.add_field(name="해역", value=pr[1], inline=True)
    embed.set_footer(text="섬 이름 클릭시 위키로 이동됨")
    return embed


lastchktime = None
lastserverstat = ""
RELOAD_TIME = 240


@bot.is_owner
@bot.command
async def 서버(ctx):
    STATURL = "https://www.seaofthieves.com/status"

    if lastchktime is None:
        cachetime = RELOAD_TIME
    else:
        cachetime = time.time() - lastchktime

    if cachetime < RELOAD_TIME:
        await ctx.send(lastserverstat)
        return None

    res = requests.get(STATURL)

    if res.status_code != 200 or res is None:
        await ctx.send("서버 상태를 확인할 수 없습니다.")
        return None

    # soup = BeautifulSoup(res.text)

    # srvinfo = soup.find("div", {"class": "service__info"})
    # h2 = srvinfo.find("h2").


@bot.event
async def on_member_join(member):
    msg = (f'{member.mention} ``!아이디`` ``xboxid`` 로 게임 내 아이디 지정하고\n'
           '규칙은 https://discord.gg/QhHZJUH 보고 겜하셈')
    ch = bot.get_channel(726374943121473627)
    await ch.send(msg)

print('봇 실행중')
bot.run(BOT_TOKEN)
