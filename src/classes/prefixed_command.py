from typing import Callable

from interactions.ext.prefixed_commands import PrefixedCommand

from src.vars import COMMAND_PREFIX


def make_usage_str(cmdname: str, *args: str, aliases=None):
    if aliases is None:
        aliases = [cmdname]
    else:
        aliases = [cmdname] + aliases
    usage = []

    if len(args) != 0:
        param = "` `".join(args)
        param = f" `{param}`"
    else:
        param = ""

    for name in aliases:
        usage.append(f"`{COMMAND_PREFIX}{name}`{param}")

    return " 또는 ".join(usage)


class NormalCommand(PrefixedCommand):
    description: str
    long_description: str

    def __init__(self, name: str, docfilename: str | None = None, has_long_desc: bool = False, *args, **kwargs):
        global normal_command_list
        normal_command_list[name] = self

        if docfilename is not None:
            with open("./src/descriptions/" + docfilename + ".txt", encoding="utf-8") as f:
                self.description = "".join(f.readlines())
            if has_long_desc:
                with open("./src/descriptions/long_" + docfilename + ".txt", encoding="utf-8") as f:
                    content = "".join(f.readlines())
                    content = content.replace("{CMD_PREFIX}", COMMAND_PREFIX)
                    self.long_description = self.description + "\n\n" + content
            else:
                self.long_description = self.description
        else:
            self.description = ""

        self.all_names = [name] + kwargs["aliases"]

        super().__init__(name=name, *args, **kwargs)


def normal_command(
    name: str | None = None,
    *args,
    aliases: list[str] | None = None,
    help: str | None = None,
    brief: str | None = None,
    usage: str | None = None,
    enabled: bool = True,
    hidden: bool = False,
    ignore_extra: bool = True,
    description_file_name: str | None = None,
    has_long_description: bool = False,
) -> Callable[..., NormalCommand]:
    def wrapper(func: Callable) -> NormalCommand:
        usage = make_usage_str(name or func.__name__, *args, aliases=aliases)
        return NormalCommand(
            docfilename=description_file_name,
            callback=func,
            name=name or func.__name__,
            aliases=aliases or [],
            has_long_desc=has_long_description,
            help=help,
            brief=brief,
            usage=usage,
            enabled=enabled,
            hidden=hidden,
            ignore_extra=ignore_extra,
        )

    return wrapper


normal_command_list: dict[str, NormalCommand] = {}
