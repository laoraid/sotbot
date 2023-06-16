from interactions import Extension, InteractionContext

from ..classes.mylogger import botlogger
from ..vars import ALLOWED_CHANNEL, ID_CHANGE_CHANNEL


class Extensionbase(Extension):
    def __init__(self, client):
        self.client = client
        self.add_ext_check(self.channel_check)
        self.add_extension_prerun(self.pre_run)

    async def channel_check(self, ctx: InteractionContext):
        chk = False
        if ctx.command.name == "아이디":
            chk = ctx.channel_id == ID_CHANGE_CHANNEL
        else:
            chk = ctx.channel.id in ALLOWED_CHANNEL

        botlogger.info(f"체크 : {chk}")
        return chk

    async def pre_run(self, ctx: InteractionContext, *args, **kwargs):
        botlogger.info(f"{ctx.user.display_name} : /{ctx.command.name} {' '.join(ctx.args)}")
