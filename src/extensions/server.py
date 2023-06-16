from interactions import OptionType, SlashContext, slash_command, slash_option
from interactions.ext.prefixed_commands import PrefixedContext

from src.classes.prefixed_command import normal_command
from src.classes.utils import make_cmd_embed
from src.extensions.extensionbase import Extensionbase
from src.extensions.serverhelper import time, xboxid


class Server(Extensionbase):
    @normal_command("도움말", aliases=["help"], description_file_name="help")
    async def help(self, ctx, *args):
        await ctx.send(embed=make_cmd_embed(args[0]))

    @normal_command("아이디", "xboxid", description_file_name="xboxid", has_long_description=True)
    async def id_prefixed(self, ctx: PrefixedContext, id: str):
        await xboxid(ctx, id)

    @slash_command(name="아이디", description="🆔 xbox 아이디가 보이게 닉네임을 변경합니다.")
    @slash_option(name="아이디", description="xbox 아이디만 입력하세요.", required=True, opt_type=OptionType.STRING)
    async def id_slash(self, ctx: SlashContext, 아이디: str):
        await xboxid(ctx, 아이디)

    @normal_command("시각", aliases=["시간", "time"], description_file_name="time")
    async def time_prefixed(self, ctx):
        await time(ctx)

    @slash_command(name="시각", description="📅 현재 시간을 시간대별로 보여줍니다.")
    async def time_slash(self, ctx):
        await time(ctx)


def setup(bot):
    Server(bot)
