import os
import difflib
import re
import datetime

from discord.ext import commands
import discord

import openpyxl

import requests
from bs4 import BeautifulSoup

try:
    BOT_TOKEN = os.environ['BOT_TOKEN']
except KeyError:
    import config
    BOT_TOKEN = config.TOKEN

bot = commands.Bot(command_prefix='!')
sheet = openpyxl.load_workbook('./islands.xlsx', data_only=True)['Sheet1']
i = 2
islandspos = {}
while (True):
    islandname = sheet.cell(row=i, column=1).value

    if islandname is None:
        break
    pos = sheet.cell(row=i, column=2).value
    region = sheet.cell(row=i, column=3).value
    engname = sheet.cell(row=i, column=4).value

    islandspos[islandname] = [pos, region, engname]
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

    substr = [x for x in islands if island in x.lower()]

    if (len(substr) == 0):
        clmat = difflib.get_close_matches(island, islands, cutoff=0.5)
        if (len(clmat) == 0):
            await ctx.send(f"``{island}`` 섬을 찾을 수 없습니다.")
            return None
        else:
            island = clmat[0]
    else:
        island = substr[0]
    await ctx.send(embed=make_pos_embed(island))


def make_pos_embed(name):
    pr = islandspos[name]
    urlname = pr[2].replace(" ", "_")
    WIKI_URL = f"https://seaofthieves.gamepedia.com/{urlname}"
    embed = discord.Embed(title=name, url=WIKI_URL)
    embed.add_field(name="좌표", value=pr[0], inline=True)
    embed.add_field(name="해역", value=pr[1], inline=True)
    embed.set_footer(text="섬 이름 클릭시 위키로 이동됨")
    return embed


lastchktime = None
lastserverstat = ""
RELOAD_TIME = datetime.timedelta(minutes=3)


@bot.command()
async def 서버(ctx):
    STATURL = "https://www.seaofthieves.com/ko/status"
    SERVER_IS_SICK = ":regional_indicator_x: 점검중이거나 서버가 터졌어요."
    SERVER_HEALTHY = ":white_check_mark: 서버가 정상이에요."
    SERVER_UNKNOWN = "서버 상태를 확인할 수 없어요."

    global lastserverstat, lastchktime

    if lastchktime is None:
        cachetime = RELOAD_TIME
    else:
        cachetime = datetime.datetime.now() - lastchktime

    if cachetime < RELOAD_TIME:
        await ctx.send(lastserverstat)
        return None

    res = requests.get(STATURL)

    if res.status_code != 200 or res is None:
        await ctx.send(SERVER_UNKNOWN)
        return None

    soup = BeautifulSoup(res.text, 'html.parser')

    srvinfo = soup.find("div", {"class": "service__info"})
    text = srvinfo.find("h2").contents[0]
    lastchktime = datetime.datetime.now()

    if text == "문제가 발생하여 서비스에 지장이 있습니다.":
        await ctx.send(SERVER_IS_SICK)
        lastserverstat = SERVER_IS_SICK
    if text == "모든 서비스가 정상 운영되고 있습니다.":
        await ctx.send(SERVER_HEALTHY)
        lastserverstat = SERVER_HEALTHY
    else:
        await ctx.send(SERVER_UNKNOWN)
        lastserverstat = SERVER_UNKNOWN


@bot.event
async def on_member_join(member):
    msg = (f'{member.mention} ``!아이디`` ``xboxid`` 로 게임 내 아이디 지정하고\n'
           '규칙은 https://discord.gg/QhHZJUH 보고 겜하셈')
    ch = bot.get_channel(726374943121473627)
    await ch.send(msg)

print('봇 실행중')
bot.run(BOT_TOKEN)
