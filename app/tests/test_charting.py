from datetime import datetime, date

from app.models import Activity
from app.services import charting


def test_calc_start_week():
    iso_date = '2020-06-18T21:58:33.302785-07:00'

    my_date = datetime.strptime(iso_date, '%Y-%m-%dT%H:%M:%S.%f%z').date()
    start_week = charting.get_start_week_date(my_date)
    assert start_week.month == 6
    assert start_week.day == 15

    iso_date = '2020-04-01T21:58:33.302785-07:00'

    my_date = datetime.strptime(iso_date, '%Y-%m-%dT%H:%M:%S.%f%z').date()
    start_week = charting.get_start_week_date(my_date)
    assert start_week.month == 3
    assert start_week.day == 30


def test_calc_start_week_offset():
    iso_date = '2020-06-18T21:58:33.302785-07:00'

    my_date = datetime.strptime(iso_date, '%Y-%m-%dT%H:%M:%S.%f%z').date()
    start_week = charting.get_start_week_date(my_date, 1)
    assert start_week.month == 6
    assert start_week.day == 8


def test_calc_day_before_start_week():
    iso_date = '2020-04-01T21:58:33.302785-07:00'
    my_date = datetime.strptime(iso_date, '%Y-%m-%dT%H:%M:%S.%f%z').date()
    start_week = charting.get_start_week_date_before(my_date)
    assert start_week.month == 3
    assert start_week.day == 29


def test_calc_day_before_start_week_offset():
    iso_date = '2020-06-18T21:58:33.302785-07:00'

    my_date = datetime.strptime(iso_date, '%Y-%m-%dT%H:%M:%S.%f%z').date()
    start_week = charting.get_start_week_date_before(my_date, 1)
    assert start_week.month == 6
    assert start_week.day == 7


def test_calc_day_before_start_week_current_date():
    start_week = charting.get_start_week_date_before(None)
    assert start_week is not None
    assert isinstance(start_week, date)


def test_calc_start_week_current_date():
    start_week = charting.get_start_week_date(None)
    assert start_week is not None
    assert isinstance(start_week, date)


def test_get_week_bookends():
    iso_date = '2020-06-18T21:58:33.302785-07:00'

    my_date = datetime.strptime(iso_date, '%Y-%m-%dT%H:%M:%S.%f%z').date()
    start_week_prior, start_week, end_week = charting.get_week_bookends(my_date)
    assert start_week_prior.month == 6
    assert start_week_prior.day == 14

    assert start_week.month == 6
    assert start_week.day == 15

    assert end_week.month == 6
    assert end_week.day == 21


def test_get_week_bookends_offset():
    iso_date = '2020-06-18T21:58:33.302785-07:00'

    my_date = datetime.strptime(iso_date, '%Y-%m-%dT%H:%M:%S.%f%z').date()
    start_week_prior, start_week, end_week = charting.get_week_bookends(my_date, week_offset=1)
    assert start_week_prior.month == 6
    assert start_week_prior.day == 7

    assert start_week.month == 6
    assert start_week.day == 8

    assert end_week.month == 6
    assert end_week.day == 14

def test_week_activity_duration_single_activity_start_week():
    iso_date = '2020-06-18T21:58:33.302785-07:00'

    my_date = datetime.strptime(iso_date, '%Y-%m-%dT%H:%M:%S.%f%z').date()
    start_week = charting.get_start_week_date(my_date)

    activity = Activity(id=1, type=1, title='title', duration=25, iso_timestamp='2020-06-15T21:58:33.302785-07:00')
    activities = [activity]

    week_duration = charting.calc_daily_duration_per_exercise_type(activities, start_week)
    assert len(week_duration) == 5
    assert len(week_duration[1]) == 7
    assert week_duration[1] == [25, 0, 0, 0, 0, 0, 0]
    for i in range(2, 6):
        assert week_duration[i] == [0, 0, 0, 0, 0, 0, 0]


def test_week_activity_duration_single_activity_end_week():
    iso_date = '2020-06-18T21:58:33.302785-07:00'

    my_date = datetime.strptime(iso_date, '%Y-%m-%dT%H:%M:%S.%f%z').date()
    start_week = charting.get_start_week_date(my_date)

    activity = Activity(id=1, type=1, title='title', duration=25, iso_timestamp='2020-06-21T21:58:33.302785-07:00')
    activities = [activity]

    week_duration = charting.calc_daily_duration_per_exercise_type(activities, start_week)
    assert len(week_duration) == 5
    assert len(week_duration[1]) == 7
    assert week_duration[1] == [0, 0, 0, 0, 0, 0, 25]


def test_week_activity_duration_single_activity_day_before_start():
    iso_date = '2020-06-18T21:58:33.302785-07:00'

    my_date = datetime.strptime(iso_date, '%Y-%m-%dT%H:%M:%S.%f%z').date()
    start_week = charting.get_start_week_date(my_date)

    activity = Activity(id=1, type=1, title='title', duration=25, iso_timestamp='2020-06-14T21:58:33.302785-07:00')
    activities = [activity]

    week_duration = charting.calc_daily_duration_per_exercise_type(activities, start_week)
    assert len(week_duration) == 5
    assert len(week_duration[1]) == 7
    assert week_duration[1] == [0, 0, 0, 0, 0, 0, 0]


def test_week_activity_duration_two_activity():
    iso_date = '2020-06-18T21:58:33.302785-07:00'

    my_date = datetime.strptime(iso_date, '%Y-%m-%dT%H:%M:%S.%f%z').date()
    start_week = charting.get_start_week_date(my_date)

    activity = Activity(id=1, type=1, title='title', duration=25, iso_timestamp='2020-06-15T21:58:33.302785-07:00')
    activity_1 = Activity(id=2, type=1, title='title', duration=32, iso_timestamp='2020-06-17T21:58:33.302785-07:00')

    activities = [activity, activity_1]

    week_duration = charting.calc_daily_duration_per_exercise_type(activities, start_week)
    assert len(week_duration) == 5
    assert len(week_duration[1]) == 7
    assert week_duration[1] == [25, 0, 32, 0, 0, 0, 0]


def test_week_activity_duration_two_activity_same_day():
    iso_date = '2020-06-18T21:58:33.302785-07:00'

    my_date = datetime.strptime(iso_date, '%Y-%m-%dT%H:%M:%S.%f%z').date()
    start_week = charting.get_start_week_date(my_date)

    activity = Activity(id=1, type=1, title='title', duration=25, iso_timestamp='2020-06-15T21:58:33.302785-07:00')
    activity_1 = Activity(id=2, type=1, title='title', duration=32, iso_timestamp='2020-06-15T05:58:33.302785-07:00')

    activities = [activity, activity_1]

    week_duration = charting.calc_daily_duration_per_exercise_type(activities, start_week)
    assert len(week_duration) == 5
    assert len(week_duration[1]) == 7
    assert week_duration[1] == [57, 0, 0, 0, 0, 0, 0]


def test_week_activity_duration_two_activity_diff_types():
    iso_date = '2020-06-18T21:58:33.302785-07:00'

    my_date = datetime.strptime(iso_date, '%Y-%m-%dT%H:%M:%S.%f%z').date()
    start_week = charting.get_start_week_date(my_date)

    activity = Activity(id=1, type=1, title='title', duration=25, iso_timestamp='2020-06-15T21:58:33.302785-07:00')
    activity_1 = Activity(id=2, type=2, title='title', duration=32, iso_timestamp='2020-06-17T05:58:33.302785-07:00')

    activities = [activity, activity_1]

    week_duration = charting.calc_daily_duration_per_exercise_type(activities, start_week)
    assert len(week_duration) == 5
    assert len(week_duration[1]) == 7
    assert week_duration[1] == [25, 0, 0, 0, 0, 0, 0]
    assert week_duration[2] == [0, 0, 32, 0, 0, 0, 0]


def test_return_chart_dataset():
    iso_date = '2020-06-18T21:58:33.302785-07:00'

    my_date = datetime.strptime(iso_date, '%Y-%m-%dT%H:%M:%S.%f%z').date()
    start_week = charting.get_start_week_date(my_date)

    activity = Activity(id=1, type=1, title='title', duration=25, iso_timestamp='2020-06-15T21:58:33.302785-07:00')
    activity_1 = Activity(id=2, type=2, title='title', duration=32, iso_timestamp='2020-06-17T05:58:33.302785-07:00')
    activity_2 = Activity(id=3, type=2, title='title', duration=32, iso_timestamp='2020-06-15T05:58:33.302785-07:00')

    activities = [activity, activity_1, activity_2]

    chart_dataset = charting.get_chart_dataset(activities, start_week)
    assert len(chart_dataset) == 2


def test_week_activity_distance_two_activity_diff_types():
    iso_date = '2020-06-18T21:58:33.302785-07:00'

    my_date = datetime.strptime(iso_date, '%Y-%m-%dT%H:%M:%S.%f%z').date()
    start_week = charting.get_start_week_date(my_date)

    activity = Activity(id=1, type=1, title='title', duration=25, distance=10, iso_timestamp='2020-06-15T21:58:33.302785-07:00')
    activity_1 = Activity(id=2, type=2, title='title', duration=32, distance=5, iso_timestamp='2020-06-17T05:58:33.302785-07:00')

    activities = [activity, activity_1]

    week_duration = charting.calc_daily_duration_per_exercise_type(activities, start_week, sum_by='distance')
    assert len(week_duration) == 5
    assert len(week_duration[1]) == 7
    assert week_duration[1] == [10, 0, 0, 0, 0, 0, 0]
    assert week_duration[2] == [0, 0, 5, 0, 0, 0, 0]


def test_week_activity_distance_end_week():
    # has an entry on the exact last day of the week
    iso_date = '2020-06-18T21:58:33.302785-07:00'

    my_date = datetime.strptime(iso_date, '%Y-%m-%dT%H:%M:%S.%f%z').date()
    start_week_prior, start_week, end_week = charting.get_week_bookends(my_date)

    activity = Activity(id=1, type=1, title='title', duration=25, distance=10, iso_timestamp='2020-06-15T21:58:33.302785-07:00')
    activity_1 = Activity(id=2, type=2, title='title', duration=32, distance=5, iso_timestamp='2020-06-21T05:58:33.302785-07:00')

    activities = [activity, activity_1]

    week_duration = charting.calc_daily_duration_per_exercise_type(activities, start_week, end_week, sum_by='distance')
    assert len(week_duration) == 5
    assert len(week_duration[1]) == 7
    assert week_duration[1] == [10, 0, 0, 0, 0, 0, 0]
    assert week_duration[2] == [0, 0, 0, 0, 0, 0, 5]


def test_week_activity_null_distance_end_week():
    # has an entry on the exact last day of the week
    iso_date = '2020-06-18T21:58:33.302785-07:00'

    my_date = datetime.strptime(iso_date, '%Y-%m-%dT%H:%M:%S.%f%z').date()
    start_week_prior, start_week, end_week = charting.get_week_bookends(my_date)

    activity = Activity(id=1, type=1, title='title', duration=25, iso_timestamp='2020-06-15T21:58:33.302785-07:00')

    activities = [activity]

    week_duration = charting.calc_daily_duration_per_exercise_type(activities, start_week, end_week, sum_by='distance')
    assert len(week_duration) == 5
    assert len(week_duration[1]) == 7
    assert week_duration[1] == [0, 0, 0, 0, 0, 0, 0]


def test_week_activity_distance_into_next_week():
    # has an entry for the day after the end of week, should not be counted
    iso_date = '2020-06-18T21:58:33.302785-07:00'

    my_date = datetime.strptime(iso_date, '%Y-%m-%dT%H:%M:%S.%f%z').date()
    start_week_prior, start_week, end_week = charting.get_week_bookends(my_date)

    activity = Activity(id=1, type=1, title='title', duration=25, distance=10, iso_timestamp='2020-06-15T21:58:33.302785-07:00')
    activity_1 = Activity(id=2, type=2, title='title', duration=32, distance=5, iso_timestamp='2020-06-22T05:58:33.302785-07:00')

    activities = [activity, activity_1]

    week_duration = charting.calc_daily_duration_per_exercise_type(activities, start_week, end_week, sum_by='distance')
    assert len(week_duration) == 5
    assert len(week_duration[1]) == 7
    assert week_duration[1] == [10, 0, 0, 0, 0, 0, 0]
    assert week_duration[2] == [0, 0, 0, 0, 0, 0, 0]


def test_week_activity_distance_positive_timezone():
    # has an entry for a timezone ahead of UTC
    iso_date = '2020-06-18T21:58:33.302785-07:00'

    my_date = datetime.strptime(iso_date, '%Y-%m-%dT%H:%M:%S.%f%z').date()
    start_week_prior, start_week, end_week = charting.get_week_bookends(my_date)

    activity = Activity(id=1, type=1, title='title', duration=25, distance=10, iso_timestamp='2020-06-15T04:58:33.302785+05:00')

    activities = [activity]

    week_duration = charting.calc_daily_duration_per_exercise_type(activities, start_week, end_week, sum_by='distance')
    assert len(week_duration) == 5
    assert len(week_duration[1]) == 7
    assert week_duration[1] == [10, 0, 0, 0, 0, 0, 0]
