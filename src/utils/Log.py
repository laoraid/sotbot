import datetime

from . import toKCT, dt_to_str


def i(ctx):
    time = toKCT(ctx.message.created_at)
    ca = dt_to_str(time, True)
    print(f"[info/{ca}] {ctx.author} | {ctx.message.content}")


def e(ctx=None, *, error):
    time = toKCT(datetime.datetime.utcnow())
    now = dt_to_str(time, True)
    if ctx is None:
        content = error
    else:
        content = f"{ctx.message.content} | {error}"
    print(f"[error/{now}] | {content}")


def v(ctx=None, v=None):
    if ctx is None:
        time = toKCT(datetime.datetime.utcnow())
        content = ""
    else:
        time = toKCT(ctx.message.created_at)
        content = ctx.message.content

    ca = dt_to_str(time, True)

    print(f"[Verbose/{ca}] {content} | {v}")
