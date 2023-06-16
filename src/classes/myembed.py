from interactions import Embed

from src.classes.utils import randcolor


class Field(object):
    def __init__(self, name: str, value: str, inline=True):
        self.name = name
        self.value = value
        self.inline = inline


class MyEmbed(Embed):
    def __init__(self, title, *fields: Field, titleurl=None, color=None, footer=""):
        if color is None:
            color = randcolor()

        if titleurl is not None:
            super().__init__(title=title, url=titleurl, color=color)
        else:
            super().__init__(title=title, color=color)

        for f in fields:
            self.add_field(name=f.name, value=f.value, inline=f.inline)

        if footer is not None:
            self.set_footer(text=footer)
