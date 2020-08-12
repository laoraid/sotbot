import re
import tossi

from discord.ext import commands

CHICKEN = 3
PIG = 4
SNAKE = 5


class Animal(commands.Converter):
    async def convert(self, ctx, arg):
        arg = arg.lower()
        if arg in ["닭", "치킨", "chicken"]:
            return CHICKEN
        elif arg in ["돼지", "pig", "피그"]:
            return PIG
        elif arg in ["뱀", "snake", "스네이크"]:
            return SNAKE
        un = tossi.postfix(arg, "은")
        raise commands.BadArgument(f"{un} 동물 종류가 아닙니다.", arg)


def convert_animal(infoarr):
    c = ""
    p = ""
    s = ""

    if infoarr[CHICKEN]:
        c = "닭"
    if infoarr[PIG]:
        p = "돼지"
    if infoarr[SNAKE]:
        s = "뱀"

    if c == "" and p == "" and s == "":
        r = "없음"
    else:
        arr = [x for x in [c, p, s] if x != ""]
        r = ",".join(arr)

    return r


class Position(commands.Converter):
    async def convert(self, ctx, arg):
        pos = arg.upper()
        pos = pos.replace("-", "")

        ispos = re.match(r"^[A-Z]{1}-*([1-9]|[0,1][0-9]|2[0-6])$", pos)
        ispos = True if ispos is not None else False

        if not ispos:
            un = tossi.postfix(arg, "은")
            raise commands.BadArgument(f"{un} 좌표가 아닙니다.", arg)

        return pos
