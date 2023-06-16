from interactions import Converter

from src.classes.data import Animal


class AnimalConverter(Converter):
    async def convert(ctx, arg):  # noqa
        return Animal(arg)
