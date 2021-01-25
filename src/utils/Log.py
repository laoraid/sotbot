import datetime
import logging
import logging.handlers

from . import toKCT, fmdate

logger = logging.getLogger("bot")
logger.setLevel(logging.DEBUG)

logger.addHandler(logging.StreamHandler())
maxbyte = 1024 * 1024 * 10
logger.addHandler(logging.handlers.RotatingFileHandler(
    "bot.log", maxBytes=maxbyte, backupCount=10))


def i(ctx):
    time = toKCT(ctx.message.created_at)
    ca = fmdate(time, True)
    logger.info(f"[info/{ca}] {ctx.author} | {ctx.message.content}")


def e(ctx=None, *, error):
    time = toKCT(datetime.datetime.utcnow())
    now = fmdate(time, True)
    if ctx is None:
        content = error
    else:
        content = f"{ctx.message.content} | {error}"
    logger.error(f"[error/{now}] | {content}")


def v(ctx=None, v=None):
    if ctx is None:
        time = toKCT(datetime.datetime.utcnow())
        content = ""
    else:
        time = toKCT(ctx.message.created_at)
        content = ctx.message.content

    ca = fmdate(time, True)

    logger.debug(f"[Verbose/{ca}] {content} | {v}")
