import random
from functools import lru_cache

from src.classes import myembed
from src.classes.data import Island
from src.classes.mylogger import botlogger
from src.classes.prefixed_command import normal_command_list


def randcolor() -> int:
    return random.randint(0, 16581375)


@lru_cache
def make_cmd_embed(cmdname) -> "myembed.MyEmbed":
    botlogger.debug(f"cmd({cmdname}) help embed 생성")
    cmd = normal_command_list[cmdname]
    return myembed.MyEmbed(
        f"{cmdname} 명령어",
        myembed.Field("설명", cmd.long_description, False),
        myembed.Field("사용법", cmd.usage),
        color=0xEEC42B,
    )


def make_pos_embed(island: Island, lang: str = "kor") -> "myembed.MyEmbed":
    return myembed.MyEmbed(
        island.getname(lang),
        myembed.Field("좌표", str(island.position)),
        myembed.Field("동물", island.animalstr),
        myembed.Field("해역", island.region, False),
        titleurl=island.wikiurl,
        color=region_color(island.region),
        footer="섬 이름 클릭 시 위키로 이동됨",
    )


def region_color(region) -> int:
    RED = 0xD22B55  # noqa
    GREEN = 0x05F445  # noqa
    GRAY = 0x7C828E  # noqa
    PURPLE = 0x620062  # noqa

    if region == "The Devil's Roar":
        return RED
    if region == "The Shores of Plenty":
        return GREEN
    if region == "The Wilds":
        return GRAY
    if region == "The Ancient Isles":
        return PURPLE

    return randcolor()
