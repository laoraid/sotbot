import datetime

import pytest
from discord.ext import commands

from src import utils
from src.config import CMD_PREFIX
from src.cogs import server


def test_mkhelpstr():
    c1 = f"`{CMD_PREFIX}테스트1`"
    c2 = f"`{CMD_PREFIX}테스트2` `인자1` `인자2`"

    assert c1 == utils.mkhelpstr("테스트1")
    assert c2 == utils.mkhelpstr("테스트2", "인자1", "인자2")


def test_datetime():
    now = datetime.datetime.utcnow()

    kct = now + datetime.timedelta(hours=9)
    kct = utils.KCT.localize(kct)
    assert kct == utils.toKCT(now)

    dt = datetime.datetime(2001, 1, 1, 1, 0, 0, 0, tzinfo=utils.KCT)
    dtstr = "2001-01-01 01:00:00"

    assert dtstr == utils.fmdate(dt)


bot = commands.Bot("!")
bot.remove_command("help")


@bot.command(description="TEST")
async def ctest1(ctx):
    pass


@bot.command(description="I'm hidden", hidden=True)
async def ctest_hidden(ctx):
    pass


@bot.command(aliases=["t2"], description="TEST2")
async def ctest2(ctx):
    pass


def test_mkhelpembed():
    utils.make_help_embed(bot)
    embed = utils.helpembed

    for f in embed.fields:
        assert f.name in ["ctest1", "ctest2, t2"]
        assert f.name != "ctest_hidden"
        assert f.value in [ctest1.description, ctest2.description]
        assert f.value != "I'm hidden"


@pytest.mark.asyncio
async def test_converter_animal():
    a = utils.converters.Animal()

    ck = await a.convert(None, "chickEn")
    assert "chicken" == ck
    assert "닭" == utils.converters.decode_animal(ck)

    assert "chicken" == await a.convert(None, "chicken")

    sn = await a.convert(None, "snAke")
    assert "snake" == sn
    assert "뱀" == utils.converters.decode_animal(sn)

    pig = await a.convert(None, "돼지")
    assert "pig" == pig
    assert "돼지" == utils.converters.decode_animal(pig)

    assert "snake" == await a.convert(None, "스네이크")
    assert "snake" == await a.convert(None, "뱀")

    with pytest.raises(ValueError):
        utils.converters.decode_animal(0)


def test_conv_animal_str():
    c1 = {"chicken": 1, "pig": 1, "snake": 1}
    assert "닭,돼지,뱀" == utils.converters.convert_animal(c1)
    c1["pig"] = 0
    assert "닭,뱀" == utils.converters.convert_animal(c1)


@pytest.mark.asyncio
async def test_converter_pos():
    p = utils.converters.Position()

    assert "A03" == await p.convert(None, "a-03")
    assert "P19" == await p.convert(None, "P19")
    assert "Z21" == await p.convert(None, "z21")


def test_regex_voicech():
    c1 = "추가 슬루프 - 213"
    c2 = "브리건틴 - 2"
    c3 = "추가 갤리온 - 1"
    c4 = "추 갤리온 14"
    c5 = "추가 g -1"

    rc1 = server._regex_voicech(c1)
    assert rc1 is not None
    assert rc1.group("name") == "슬루프"
    assert rc1.group("num") == "213"
    rc2 = server._regex_voicech(c2)
    assert rc2 is not None
    assert rc2.group("name") == "브리건틴"
    assert rc2.group("num") == "2"
    rc3 = server._regex_voicech(c3)
    assert rc3 is not None
    assert rc3.group("name") == "갤리온"
    assert rc3.group("num") == "1"
    assert server._regex_voicech(c4) is None
    assert server._regex_voicech(c5) is None


@pytest.mark.asyncio
async def test_conv_Ship():
    s = utils.converters.Ship()
    assert {"name": "갤리온", "id": 0} == await s.convert(None, "GAlLeOn")
    assert {"name": "브리건틴", "id": 1} == await s.convert(None, "브리간틴")
    assert {"name": "슬루프", "id": 2} == await s.convert(None, "SLoOP")

    with pytest.raises(commands.BadArgument):
        await s.convert(None, "asdafe")
