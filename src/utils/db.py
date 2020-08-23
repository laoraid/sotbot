import sqlite3

from . import mkEmptyList


class DB(object):
    def __init__(self, filename):
        self.filename = filename

    def connect(self):
        self.connenct = sqlite3.connect(self.filename)
        self.cur = self.connenct.cursor()

    def query(self, query):
        self.cur.execute(query)
        return self.cur.fetchall()

    def select_where(self, field, table, where):
        query = f"select {field} from {table} where {where}"
        return self.query(query)

    def field(self, tablename, fname):
        return self.query(f"select {fname} from {tablename}")

    def __enter__(self):
        self.connect()

    def __exit__(self, exc_type, exc_value, traceback):
        self.connenct.close()

    def makedict(self, names, data):
        d = {}
        for i, name in enumerate(names):
            if data[i] is not None:
                d[name] = data[i]

        return d


class IslandDB(DB):
    def __init__(self):
        super(IslandDB, self).__init__("src/data/old/island.db")

    def _dict(self, *, krname=None, pos=None, engname=None,
              region=None, ch=None, pig=None, snake=None):
        names = ["krname", "pos", "region",
                 "engname", "chicken", "pig", "snake"]
        data = [krname, pos, engname, region, ch, pig, snake]
        return self.makedict(names, data)

    def field(self, fieldname):
        r = super(IslandDB, self).field("islands", fieldname)
        r = [x[0] for x in r]
        return r

    def select_where(self, field, where):
        return super(IslandDB, self).select_where(field, "islands", where)

    def _dictall(self, data):
        names = ["krname", "pos", "region",
                 "engname", "chicken", "pig", "snake"]
        return self.makedict(names, data)

    def get_data_by_name(self, lang, name):
        if lang.lower() == "kr":
            where = f"KRname='{name}'"
        elif lang.lower() == "eng":
            where = f"Engname='{name}'"

        return self._dictall(self.select_where("*", where)[0])

    def get_data_by_animal(self, animals):
        where = []

        for animal in animals:
            where.append(f"{animal}=1")

        where = " and ".join(where)
        raw = self.select_where("*", where)
        arr = mkEmptyList(len(raw))

        for i, data in enumerate(raw):
            arr[i] = self._dictall(data)
        return arr
