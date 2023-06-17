import os
import traceback
from functools import lru_cache

from interactions import Client, listen
from interactions.api.events import CommandError
from interactions.client import errors

from src.classes.error import NotAnimalStringError, NotPositionStringError
from src.classes.myembed import Field, MyEmbed
from src.classes.mylogger import botlogger
from src.classes.prefixed_command import normal_command_list
from src.classes.utils import make_cmd_embed
from src.vars import COMMAND_PREFIX, OWNER_ID

# load_exteonsions method from interactions.py example.
# https://github.com/NAFTeam/Bot-Template/blob/main/%7B%7B%20cookiecutter.project_slug%20%7D%7D/core/extensions_loader.py


def get_traceback(error) -> str:
    trace = traceback.format_exception(type(error), error, error.__traceback__)
    tracestr = "".join(trace)
    return tracestr


class Sotbot(Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @listen()
    async def on_startup(self):
        botlogger.info(f"봇 실행중 서버 : {len(self.guilds)}개")

    def load_extensions(self):
        for root, dirs, files in os.walk("src/extensions"):
            for file in files:
                if file.endswith(".py") and not (
                    file.startswith("__init__") or file.startswith("extensionbase") or file.endswith("helper.py")
                ):
                    file = file.removesuffix(".py")
                    path = os.path.join(root, file)
                    python_import_path = path.replace("/", ".").replace("\\", ".")

                    self.load_extension(python_import_path)
                    botlogger.info(f"확장 불러옴 : {python_import_path}")

    @listen(disable_default_listeners=True)
    async def on_command_error(self, event: CommandError):
        error = event.error
        botlogger.info(f"오류 처리 : {type(error)}")
        if isinstance(error, errors.CommandCheckFailure):
            await event.ctx.send("이 채널에서 사용할 수 없습니다.")
        elif isinstance(error, errors.BadArgument):
            cmdname = event.ctx.command.name
            if cmdname == "도움말":
                await event.ctx.send(embed=self.make_help_embed())
            elif str(error).endswith("1"):
                await event.ctx.send(str(error)[:-1] + f" 도움말 : `{COMMAND_PREFIX}help {cmdname}`")
            else:
                await event.ctx.send(embed=make_cmd_embed(cmdname))
        elif isinstance(error, (NotPositionStringError, NotAnimalStringError)):
            await event.ctx.send(str(error)[:-1])
        elif isinstance(error, errors.Forbidden):
            await event.ctx.send("권한 부족")
            traceback = get_traceback(error)
            botlogger.warning(traceback)
        else:
            traceback = get_traceback(error)
            botlogger.error(traceback)
            owner = await self.fetch_user(OWNER_ID)
            await owner.send(f"에러 발생 : {type(error)}\n{traceback}")

    @lru_cache
    def make_help_embed(self):
        botlogger.debug("help embed 생성")

        fields = []

        for cmd in normal_command_list.values():
            fields.append(Field(name=", ".join(cmd.all_names), value=cmd.description, inline=False))

        return MyEmbed("명령어 리스트", *fields, footer=f"{COMMAND_PREFIX}help 명령어 입력 시 개별 명령어 도움말 출력", color=0x2BA3EE)
