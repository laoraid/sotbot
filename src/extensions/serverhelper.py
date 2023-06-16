import re

from interactions import BaseContext

from src.classes.myembed import Field, MyEmbed
from src.classes.time import BST, KCT, PST, UTC, get_time


async def time(ctx):
    embed = MyEmbed(
        "현재 시각은...",
        Field("KCT", get_time(KCT), False),
        Field("UTC/GMT", get_time(UTC), False),
        Field("BST", get_time(BST), False),
        Field("PST", get_time(PST), False),
        color=5234869,
    )

    await ctx.send(embed=embed)


async def xboxid(ctx: BaseContext, id):
    prevnick = ctx.author.display_name
    pattern = r"(?P<nickname>\S+)\s*\(.+\)"

    mat = re.match(pattern, prevnick)

    if mat is not None:
        nick = f'{mat.group("nickname")}({id})'
    else:
        nick = f"{prevnick}({id})"

    if len(nick) > 32:
        await ctx.send(f"{ctx.author.mention} 닉네임이 너무 깁니다.")
        return

    await ctx.author.edit(nickname=nick)
    await ctx.send(f"`{prevnick}`의 닉네임이 `{nick}`으로 변경되었습니다.")
