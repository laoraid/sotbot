import datetime
import sqlite3

from . import mkEmptyList


class DB(object):
    def __init__(self, filename):
        self.filename = filename

    def connect(self):
        self.con = sqlite3.connect(self.filename)
        self.cur = self.con.cursor()

    def query(self, query):
        self.cur.execute(query)
        return self.cur.fetchall()

    def insert(self, table, fields, data):
        fields = ",".join(fields)
        data = ",".join(data)
        query = f"insert into {table}({fields}) values ({data})"
        self.cur.execute(query)
        self.con.commit()

    def update(self, table, field, data, where, wheredata):
        query = (f"update {table} set {field}=('{data}') "
                 f"where {where} = '{wheredata}'")
        self.query(query)

    def delete(self, table, where, wheredata):
        query = f"delete from {table} where {where}='{wheredata}'"
        self.cur.execute(query)
        self.con.commit()

    def select(self, field, table):
        query = f"select {field} from {table}"
        return self.query(query)

    def select_where(self, field, table, where):
        query = f"select {field} from {table} where {where}"
        return self.query(query)

    def field(self, tablename, fname):
        return self.query(f"select {fname} from {tablename}")

    def close(self):
        self.cur.close()
        self.con.close()

    def __enter__(self):
        self.connect()

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def makedict(self, names, data):
        d = {}
        for i, name in enumerate(names):
            if data[i] is not None:
                d[name] = data[i]

        return d


class IslandDB(DB):
    def __init__(self):
        super(IslandDB, self).__init__("src/data/island.db")

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
        name = name.replace("'", "''")
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


class Drops(object):
    def __init__(self, reward, startdate, enddate):
        self.reward = reward
        # self.imageurl = imageurl
        self.startdate = startdate
        self.enddate = enddate


class TwitchDropsDB(DB):
    def __init__(self):
        super(TwitchDropsDB, self).__init__("src/data/twitch_drops.db")

    def insert(self, title, drops):
        dt = datetime.datetime.utcnow()
        title = title.replace("'", "\'")

        self.cur.execute(("insert into drops(title, updateddate)"
                          " values (?,?)"),
                         (title, dt))
        self.con.commit()
        self.cur.execute(
            "select drop_id from drops where title = (?)", (title,))
        key = self.cur.fetchall()[-1][0]

        for drop in drops:
            self.cur.execute(("insert into dropsdata"
                              " (drop_id, item, startdate, enddate)"
                              " values (?, ?, ?, ?)"),
                             (key, drop.reward, drop.startdate, drop.enddate))

        self.con.commit()

    @property
    def last(self):
        q = ("select title, updateddate, item, startdate, enddate from drops"
             " inner join dropsdata on dropsdata.drop_id = drops.drop_id"
             " where updateddate = (select max(updateddate) from drops)"
             " order by startdate")
        data = self.query(q)

        if len(data) == 0:
            return None

        title = data[0][0]
        dropsdata = []
        for d in data:
            startdt = datetime.datetime.strptime(d[3], "%Y-%m-%d %H:%M:%S.%f")
            enddt = datetime.datetime.strptime(d[4], "%Y-%m-%d %H:%M:%S.%f")
            dropsdata.append(Drops(d[2], startdt, enddt))

        return (title, dropsdata)
