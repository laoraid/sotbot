import difflib
import math
import re

from ..utils import db
from ..utils.converters import convert_animal


class IslandNotFound(Exception):
    pass


class AnimalNotFound(Exception):
    pass


class IslandFinder(object):
    def __init__(self):
        self.db = db.IslandDB()
        self.db.connect()

    def close(self):
        self.db.close()

    def close_island(self, pos, animals):
        def get_int(pos):
            x = ord(pos[0])
            y = int(pos[1:])
            return (x, y)

        def get_distance(x1, y1, x2, y2):
            dx = (x1 - x2) ** 2
            dy = (y1 - y2) ** 2

            return math.sqrt(dx + dy)

        stx, sty = get_int(pos)
        islands = self.db.get_data_by_animal(animals)

        if len(islands) == 0:
            return None

        distemp = 9999
        islandtemp = ""

        for island in islands:
            isx, isy = get_int(island["pos"].replace("-", ""))
            dis = get_distance(stx, sty, isx, isy)
            if distemp > dis:
                distemp = dis
                islandtemp = island["krname"]

        return self._get_island_data(islandtemp, False)

    def _get_island_data(self, island, iseng, useddiff=False):
        if iseng:
            data = self.db.get_data_by_name("eng", island)
        else:
            data = self.db.get_data_by_name("kr", island)
        urlname = data["engname"].replace(" ", "_")
        wikiurl = f"https://seaofthieves.gamepedia.com/{urlname}"
        return dict(islandname=island, iseng=iseng, useddiff=useddiff,
                    pos=data["pos"], animal=convert_animal(data),
                    region=data["region"], wikiurl=wikiurl)

    def findisland(self, island):
        iseng = re.match(r'[^ㄱ-ㅎㅏ-ㅣ가-힣]', island)
        iseng = True if iseng is not None else False

        if iseng:
            islands = self.db.field("Engname")
        else:
            islands = self.db.field("KRname")

        substr = [x for x in islands if re.search(rf"\b{island}\b", x.lower())]
        if len(substr) == 0:
            substr = [x for x in islands if island in x.lower()]

        if len(substr) == 0:
            clmat = difflib.get_close_matches(island, islands, cutoff=0.4)
            if len(clmat) == 0:
                return None
            else:
                island = clmat[0]
                useddiff = True
        else:
            island = substr[0]
            useddiff = False

        return self._get_island_data(island, iseng, useddiff)


class singleton(type):
    _instance = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instance:
            cls._instance[cls] = super(
                singleton, cls).__call__(*args, **kwargs)
        return cls._instance[cls]
