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


class Fish(commands.Converter):
    async def convert(self, ctx, arg):
        arg = arg.lower()

        if arg in ["스플래쉬테일", "스플레시테일", "스플레쉬테일", "스플래시테일", "splashtail"]:
            return "스플래쉬테일"
        elif arg in ["플렌티핀", "플랜티핀", "plentifins"]:
            return "플렌티핀"
        elif arg in ["앤션트스케일", "엔션트스케일", "앤션트스캐일", "엔션트스캐일", "ancientscales"]:
            return "앤션트스케일"
        elif arg in ["와일드스플래쉬", "와일드스플래시", "와일드스플레쉬", "wildsplashes"]:
            return "와일드스플래쉬"
        elif arg in ["데빌피쉬", "데빌피시", "devilfish"]:
            return "데빌피쉬"
        elif arg in ["아일호퍼", "islehoppers"]:
            return "아일호퍼"
        elif arg in ["폰디", "pondies"]:
            return "폰디"
        elif arg in ["배틀길", "battlegills"]:
            return "배틀길"
        elif arg in ["스톰피쉬", "스톰피시", "stormfish"]:
            return "스톰피쉬"
        elif arg in ["래커", "레커", "wreckers"]:
            return "래커"

        arg = tossi.postfix(arg, "는")
        raise commands.BadArgument(f"{arg} 물고기 종류가 아닙니다.")
