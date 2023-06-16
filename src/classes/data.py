import difflib
import math
import re
from enum import Enum

from openpyxl import load_workbook

from src.classes.error import NoIslandNameError, NotAnimalStringError, NotPositionStringError, PositionMismatchError
from src.classes.mylogger import botlogger


class Animal(object):
    englist = ["chicken", "pig", "snake"]
    korlist = ["닭", "돼지", "뱀"]

    def __init__(self, name: str):
        if name in Animal.korlist:
            self._name = Animal.englist[Animal.korlist.index(name)]
        elif name in Animal.englist:
            self._name = name
        else:
            raise NotAnimalStringError(f"`{name}` 은 동물 이름이 아닙니다.1")

        self._korname = Animal.korlist[Animal.englist.index(self._name)]

    @property
    def name(self) -> str:
        return self._name

    @property
    def korname(self) -> str:
        return self._korname

    def __repr__(self) -> str:
        return f"Animal({self._name})"

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other) -> bool:
        if isinstance(other, str):
            other = Animal(other)
        return self._name == other._name

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def __str__(self) -> str:
        return self._korname

    @classmethod
    async def convert(cls, ctx, value) -> "Animal":
        return cls(value)


class Position(object):
    def __init__(self, x: str, y: int):
        self.x = x.upper()
        self.y = y

    def __str__(self) -> str:
        return f"{self.x}-{self.y}"

    def __repr__(self):
        return f"Position({self.x}, {self.y})"

    def __eq__(self, other) -> bool:
        if isinstance(other, str):
            other = Position.from_str(other)
        return self.x == other.x and self.y == other.y

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def distance(self, other) -> float:
        x = ord(self.x)
        y = self.y

        ox = ord(other.x)
        oy = other.y

        dx = (x - ox) ** 2
        dy = (y - oy) ** 2

        return math.sqrt(dx + dy)

    @classmethod
    def from_str(cls, string: str) -> "Position":
        string = string.upper()
        string = string.replace("-", "")
        posmatch = re.match(r"^[A-Z]{1}-*([1-9]|[0,1][0-9]|2[0-6])$", string)

        if posmatch is None:
            raise NotPositionStringError(f"`{string}`은 좌표가 아닙니다.1")

        x = string[:1]
        y = string[1:]

        return Position(x, int(y))

    @classmethod
    async def convert(cls, ctx, value) -> "Position":
        return cls.from_str(value)


class Island(object):  # animals order : chicken, pig, snake
    def __init__(self, korname: str, position: str, region: str, engname: str, *animals: str):
        self.korname = korname
        self.engname = engname
        self.position = Position.from_str(position)
        self.region = region

        self.animals = [Animal(Animal.englist[i]) for i, x in enumerate(animals) if x == "yes"]

        urlname = engname.replace(" ", "_")
        self.wikiurl = f"https://seaofthieves.gamepedia.com/{urlname}"

    def __contains__(self, animals) -> bool:
        panimals = set([Animal(x) for x in animals])
        sanimals = set(self.animals)

        if (panimals & sanimals) == panimals:
            return True
        else:
            return False

    def getname(self, lang: str = "kor") -> str:
        if lang == "kor":
            return self.korname
        return self.engname

    @property
    def animalstr(self) -> str:
        if not self.animals:
            return "없음"
        else:
            return ", ".join(x.korname for x in self.animals)


class SearchType(Enum):
    match = 0
    substr = 1
    closematch = 2
    fail = 3


class Islandxl(object):
    data: list[Island]

    def __init__(self):
        filename = "src/data/islands.xlsx"
        wb = load_workbook(filename, data_only=True)
        botlogger.debug("엑셀 불러옴")

        islands_sheet = wb["KOR"]
        islands = []
        for row in list(islands_sheet.rows)[1:]:
            islands.append([x.value for x in row])

        self.data = []
        for island in islands:
            self.data.append(Island(*island))

        self._engnames = [x.getname("eng") for x in self.data]
        self._kornames = [x.getname("kor") for x in self.data]

        botlogger.debug(f"엑셀 불러오기 완료. 개수 : {len(self._engnames)}")

    def find_by_name(self, lang: str, name: str) -> Island:
        for island in self.data:
            if island.getname(lang) == name:
                return island

        raise NoIslandNameError(f"{lang} / {name} 섬은 없습니다.")

    def find_by_pos(self, pos: str) -> Island:
        for island in self.data:
            if island.position == pos:
                return island

        raise PositionMismatchError(f"{pos}는 없는 섬입니다.")

    def finds_by_animals(self, animals: list[str]) -> list[Island]:
        return [x for x in self.data if animals in x]

    def names(self, lang: str) -> list[str]:
        if lang == "eng":
            return self._engnames
        else:
            return self._kornames

    def searches_by_name(self, name: str, cutoff=0.4) -> tuple[list[Island] | None, SearchType]:
        iseng = re.match(r"[^ㄱ-ㅎㅏ-ㅣ가-힣]", name)
        lang = "eng" if iseng is not None else "kor"

        if name in self.names(lang):
            botlogger.info(f"섬 검색 일치 : {name}")
            return [self.find_by_name(lang, name)], SearchType.match

        substr = [x for x in self.names(lang) if name.replace(" ", "") in x.lower().replace(" ", "")]
        searchtype = SearchType.substr

        if len(substr) == 0:
            result = difflib.get_close_matches(name, self.names(lang), cutoff=cutoff)
            if len(result) == 0:
                botlogger.info(f"검색 실패 : {name}")
                return None, SearchType.fail
            else:
                searchtype = SearchType.closematch
                botlogger.info(f"유사도 일치 부분 : {name}, 매치1 : {result[0]}, 컷오프 : {cutoff}")
        else:
            result = substr
            botlogger.info(f"섬 검색 부분 문자열 일치 부분 : {name}, 매치1 : {result[0]}")

        botlogger.debug(f"전체 검색 결과 : {', '.join(result)}")

        return [self.find_by_name(lang, x) for x in result], searchtype
