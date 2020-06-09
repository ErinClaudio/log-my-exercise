
from app.services import utils


def get_tz_hour_offset(my_date):
    return int(my_date[-4:-3])


def test_utils_date_notz():
    current_date = utils.get_local_time_iso()
    assert get_tz_hour_offset(current_date) == 0


def test_utils_date_invalidtz():
    current_date = utils.get_local_time_iso('asddas')
    assert get_tz_hour_offset(current_date) == 0


def test_utils_date_tz():
    west_coast = utils.get_local_time_iso('America/Los_Angeles')
    east_coast = utils.get_local_time_iso('America/Chicago')
    assert get_tz_hour_offset(west_coast) - get_tz_hour_offset(east_coast) > 0
