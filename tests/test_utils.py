import datetime

from src import utils
from src.config import CMD_PREFIX

def test_mkhelpstr():
    c1 = f"``{CMD_PREFIX}테스트1``"
    c2 = f"``{CMD_PREFIX}테스트2`` ``인자1`` ``인자2``"

    assert c1 == utils.mkhelpstr("테스트1")
    assert c2 == utils.mkhelpstr("테스트2", "인자1", "인자2")
    
def test_datetime():
    now = datetime.datetime.utcnow()

    kct = now + datetime.timedelta(hours=9)
    kct = utils.KCT.localize(kct)
    assert kct == utils.toKCT(now)

    dt = datetime.datetime(2001, 1, 1, 1, 0, 0, 0, tzinfo=utils.KCT)
    dtstr = "2001-01-01 01:00:00"

    assert dtstr == utils.dt_to_str(dt)