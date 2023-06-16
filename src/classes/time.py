from datetime import datetime

import pytz

KCT = pytz.timezone("Asia/Seoul")
UTC = pytz.utc
BST = pytz.timezone("Europe/London")
PST = pytz.timezone("America/Los_Angeles")


def _date_format(date: datetime, include_timezone=False) -> str:
    days = ["일", "월", "화", "수", "목", "금", "토"]
    tz = ""
    if include_timezone:
        tz = " %Z%z"
    day = date.strftime("%w")
    format = f"%Y년 %m월 %d일 {days[int(day)]}요일 %H시 %M분 %S초{tz}"
    format = format.encode("unicode-escape").decode()

    dstr = date.strftime(format).encode().decode("unicode-escape")
    return dstr


def get_time(timezone) -> str:
    utcnow = UTC.localize(datetime.utcnow())
    if timezone != UTC:
        time = utcnow.astimezone(timezone)
    else:
        time = utcnow

    return _date_format(time)
