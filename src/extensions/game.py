from asyncio import TimeoutError

from interactions import (
    ActionRow,
    AutocompleteContext,
    Button,
    ButtonStyle,
    OptionType,
    SlashContext,
    StringSelectMenu,
    StringSelectOption,
    slash_command,
    slash_option,
)

from src.classes.data import Animal, Islandxl, Position
from src.classes.prefixed_command import normal_command
from src.extensions.extensionbase import Extensionbase
from src.extensions.gamehelper import animalhelper, islandhelper


class Game(Extensionbase):
    def __init__(self, bot):
        super().__init__(bot)
        self.db = Islandxl()
        self.island_auto_list = [{"name": x, "value": x} for x in self.db.names("kor")]

    @slash_command(name="좌표", description="🏝️ 섬을 검색합니다.")
    @slash_option(name="이름", description="섬 이름", required=True, opt_type=OptionType.STRING, autocomplete=True)
    async def island_slash(self, ctx, 이름: str):
        await islandhelper(ctx, 이름, self.db, self.bot)

    @slash_command(name="동물", description="🐖 현재 위치에서 동물이 있는 섬을 찾습니다.")
    @slash_option(name="좌표", description="현재 좌표입니다. 예) C-1, A6", required=True, opt_type=OptionType.STRING)
    async def animal_slash(self, ctx: SlashContext, 좌표: Position):
        pos = 좌표

        animalselectmenu = StringSelectMenu(
            StringSelectOption(label="닭", value="닭", emoji="🐔"),
            StringSelectOption(label="돼지", value="돼지", emoji="🐖"),
            StringSelectOption(label="뱀", value="뱀", emoji="🐍"),
            placeholder="동물을 선택해 주세요. (최대 2가지)",
            min_values=1,
            max_values=2,
            custom_id="animal_select_menu",
        )

        cancelbtn = Button(style=ButtonStyle.DANGER, label="안할래요", emoji="🙅‍♂️", custom_id="animal_no_btn")

        components = [
            ActionRow(animalselectmenu),
            ActionRow(cancelbtn),
        ]

        msg = await ctx.send(components=components)

        try:
            usedcomp = await self.bot.wait_for_component(components=components, timeout=50)
        except TimeoutError:
            return
        finally:
            animalselectmenu.disabled = True
            cancelbtn.disabled = True
            await msg.edit(components=components)

        if usedcomp.ctx.invoke_target == animalselectmenu.custom_id:
            animals = [Animal(x) for x in usedcomp.ctx.values]
            await animalhelper(usedcomp.ctx, pos, animals, self.db, self.bot)
        else:
            return

    @normal_command("좌표", "섬 이름", aliases=["pos"], description_file_name="pos")
    async def island_prefixed(self, ctx, *, arg):
        await islandhelper(ctx, arg, self.db, self.bot)

    @island_slash.autocomplete("이름")
    async def island_autocomplete(self, ctx: AutocompleteContext):
        startswith = ctx.input_text
        auto_list = [{"name": x, "value": x} for x in self.db.names("kor") if x.startswith(startswith)]

        if len(auto_list) > 25:
            auto_list = auto_list[:25]

        await ctx.send(choices=auto_list)

    @normal_command("동물", "현재 좌표", "동물1", "동물2", description_file_name="animal", has_long_description=True)
    async def animal_prefixed(
        self,
        ctx,
        pos: Position,
        animal1: Animal,
        animal2: Animal | None,
    ):
        animals = [animal1]
        if animal2 is not None:
            animals.append(animal2)
        await animalhelper(ctx, pos, animals, self.db, self.bot)


def setup(bot):
    Game(bot)
