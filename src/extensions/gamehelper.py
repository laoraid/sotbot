from interactions import ActionRow, Button, ButtonStyle, Client, SlashContext, StringSelectMenu

from src.classes.data import Animal, Island, Islandxl, Position, SearchType
from src.classes.utils import make_pos_embed


async def islandhelper(ctx: SlashContext, name: str, db: Islandxl, bot: Client):
    result, searchtype = db.searches_by_name(name)

    if searchtype == SearchType.fail:
        await ctx.send(f"`{name}` 섬을 찾을 수 없습니다.")
        return

    await island_sender(ctx, searchtype, result, db, bot)


async def island_sender(ctx, searchtype, result: list[Island], db: Islandxl, bot: Client):
    if searchtype != SearchType.match:
        button = Button(
            style=ButtonStyle.PRIMARY,
            emoji="🙅‍♂️",
            label="내가 찾던 섬이 아니에요",
        )
    else:
        button = None

    msg = await ctx.send(embed=make_pos_embed(result[0]), components=button)

    if button is None:
        return

    try:
        usedcomp = await bot.wait_for_component(components=button, timeout=50)
    except TimeoutError:
        return
    finally:
        button.disabled = True
        await msg.edit(components=[])

    if len(result) == 1:
        await usedcomp.ctx.send("이 이름으로 더 섬을 찾을 수 없습니다. 다시 검색해 주세요.")
        return
    if len(result[1:]) > 25:
        result = result[1:26]
    else:
        result = result[1:]

    result_str = [x.korname + f", {str(x.position)}" for x in result]

    selectmenu = StringSelectMenu(*result_str, placeholder="이 중에서 골라주세요.", max_values=1, custom_id="menu")
    cancelbtn = Button(style=ButtonStyle.DANGER, label="여기에 없어요.", emoji="😦", custom_id="cancelbtn")
    selectmenuandbtn = [
        ActionRow(selectmenu),
        ActionRow(cancelbtn),
    ]
    msg = await usedcomp.ctx.send(components=selectmenuandbtn)

    try:
        usedcomp = await bot.wait_for_component(components=selectmenuandbtn, timeout=50)
    except TimeoutError:
        return
    finally:
        selectmenu.disabled = True
        cancelbtn.disabled = True
        await msg.edit(components=selectmenu)

    if usedcomp.ctx.invoke_target == cancelbtn.custom_id:
        await usedcomp.ctx.send("이 이름으로 더 섬을 찾을 수 없습니다. 다시 검색해 주세요.")
    else:
        islandname = usedcomp.ctx.values[0].split(",")[0]
        await usedcomp.ctx.send(embed=make_pos_embed(db.find_by_name("kor", islandname)))


async def animalhelper(ctx, pos: Position, animals: list[Animal], db: Islandxl, bot: Client):
    islands = db.finds_by_animals(animals)

    islands.sort(key=lambda x: x.position.distance(pos))

    await island_sender(ctx, SearchType.closematch, islands, db, bot)
