import datetime

import pytest
from discord.ext import commands

from src import utils
from src.config import CMD_PREFIX


def test_mkhelpstr():
    c1 = f"``{CMD_PREFIX}테스트1``"
    c2 = f"``{CMD_PREFIX}테스트2`` ``인자1`` ``인자2``"

    assert c1 == utils.mkhelpstr("테스트1")
    assert c2 == utils.mkhelpstr("테스트2", "인자1", "인자2")


def test_datetime():
    now = datetime.datetime.utcnow()

    kct = now + datetime.timedelta(hours=9)
    kct = utils.KCT.localize(kct)
    assert kct == utils.toKCT(now)

    dt = datetime.datetime(2001, 1, 1, 1, 0, 0, 0, tzinfo=utils.KCT)
    dtstr = "2001-01-01 01:00:00"

    assert dtstr == utils.dt_to_str(dt)


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

    assert 3 == await a.convert(None, "chickEn")
    assert 3 == await a.convert(None, "닭")
    assert 5 == await a.convert(None, "snAke")
    assert 4 == await a.convert(None, "돼지")
    assert 5 == await a.convert(None, "스네이크")
    assert 5 == await a.convert(None, "뱀")

    with pytest.raises(commands.BadArgument):
        await a.convert(None, "asdafe")


def test_conv_animal_str():
    assert "닭,돼지,뱀" == utils.converters.convert_animal([True] * 6)
    assert "닭,뱀" == utils.converters.convert_animal(
        [0, 0, 0, True, False, True])


@pytest.mark.asyncio
async def test_converter_pos():
    p = utils.converters.Position()

    assert "A03" == await p.convert(None, "a-03")
    assert "P19" == await p.convert(None, "P19")
    assert "Z21" == await p.convert(None, "z21")

    with pytest.raises(commands.BadArgument):
        await p.convert(None, "www1")
        await p.convert(None, "A-29")
        await p.convert(None, "q39")
