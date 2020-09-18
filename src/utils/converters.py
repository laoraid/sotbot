import re
import tossi

from discord.ext import commands

from ..utils import str_help_by_cmd


class Animal(commands.Converter):
    async def convert(self, ctx, arg):
        arg = arg.lower()
        if arg in ["닭", "치킨", "chicken"]:
            return "chicken"
        elif arg in ["돼지", "pig", "피그"]:
            return "pig"
        elif arg in ["뱀", "snake", "스네이크"]:
            return "snake"
        un = tossi.postfix(arg, "은")
        cmdname = ctx.command
        helpstr = str_help_by_cmd(cmdname)
        raise commands.BadArgument(f"{un} 동물 종류가 아닙니다. {helpstr}", arg)


def convert_animal(data):
    c = ""
    p = ""
    s = ""

    if data["chicken"] == 1:
        c = "닭"
    if data["pig"] == 1:
        p = "돼지"
    if data["snake"] == 1:
        s = "뱀"

    if c == "" and p == "" and s == "":
        r = "없음"
    else:
        arr = [x for x in [c, p, s] if x != ""]
        r = ",".join(arr)

    return r


def decode_animal(a):
    if a == "chicken":
        return "닭"
    elif a == "snake":
        return "뱀"
    elif a == "pig":
        return "돼지"
    raise ValueError


class Position(commands.Converter):
    async def convert(self, ctx, arg):
        pos = arg.upper()
        pos = pos.replace("-", "")

        ispos = re.match(r"^[A-Z]{1}-*([1-9]|[0,1][0-9]|2[0-6])$", pos)
        ispos = True if ispos is not None else False

        if not ispos:
            un = tossi.postfix(arg, "은")
            cmdname = ctx.command
            helpstr = str_help_by_cmd(cmdname)
            raise commands.BadArgument(f"{un} 좌표가 아닙니다. {helpstr}", arg)

        return pos


GALLEON = 0
BRIG = 1
SLOOP = 2


class Ship(commands.Converter):
    async def convert(self, ctx, arg):
        arg = arg.lower()

        if arg in ["갤리온", "갤리언", "galleon"]:
            return {"name": "갤리온", "id": GALLEON}
        elif arg in ["브리건틴", "브리건타인", "브리간틴", "brigantine"]:
            return {"name": "브리건틴", "id": BRIG}
        elif arg in ["슬루프", "sloop"]:
            return {"name": "슬루프", "id": SLOOP}

        arg = tossi.postfix(arg, "는")
        raise commands.BadArgument(f"{arg} 배 종류가 아닙니다.")
