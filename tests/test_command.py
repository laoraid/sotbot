import pytest

from tests import testctx
from src.cogs import game, manage
from src import utils
from src import config


ctx = testctx.ctx()
g = game.Game(None)
m = manage.Manage(None)


@pytest.mark.asyncio
async def test_pos():
    callback = getattr(g.좌표, "callback")
    await callback(g, ctx=ctx, island="reaper")
    embed = ctx.lastembed

    island = "The Reaper's Hideout"
    pos = "I-12"
    animal = "없음"
    region = "The Reaper's Hideout"

    chk_pos_embed(embed, island, pos, animal, region)
    url = r"https://seaofthieves.gamepedia.com/The_Reaper's_Hideout"
    assert embed.url == url


def chk_pos_embed(embed, island, pos, animal, region):
    assert embed.title == island

    for f in embed.fields:
        assert f.name in ["좌표", "동물", "해역"]
        if f.name == "좌표":
            assert f.value == pos
        elif f.name == "동물":
            assert f.value == animal
        elif f.name == "해역":
            assert f.value == region


@pytest.mark.asyncio
async def test_animal():
    callback = getattr(g.동물, "callback")

    await callback(g, ctx=ctx, p="Q17", n=[3])

    embed = ctx.lastembed
    island = "따개비 케이"
    pos = "O-15"
    animal = "닭"
    region = "The Ancient Isles"

    chk_pos_embed(embed, island, pos, animal, region)


@pytest.mark.asyncio
async def test_server():
    callback = getattr(g.서버, "callback")

    await callback(g, ctx)


def test_help():
    embed = utils.make_cmd_help_embed(g.동물)
    ld = config.LONG_DESCRIPTIONS["동물"]

    usage = getattr(g.동물, "usage")

    assert embed.title == "동물 명령어"

    for f in embed.fields:
        assert f.name in ["설명", "사용법"]

        if f.name == "설명":
            assert f.value == ld
        elif f.name == "사용법":
            assert f.value == usage
