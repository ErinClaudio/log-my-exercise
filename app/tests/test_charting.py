from datetime import datetime, date

import pytest

from app.models import Activity, Goal
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


def test_get_date_from_isotimestamp():
    iso_date = '2020-06-18T21:58:33.302785-07:00'

    local_date = charting.get_date_from_isotimestamp(iso_date, None)
    assert local_date.day == 18
    assert local_date.month == 6
    assert local_date.year == 2020


def test_get_date_from_blank_isotimestamp():
    local_date = charting.get_date_from_isotimestamp(None, datetime(2020, 6, 18))
    assert local_date.day == 18
    assert local_date.month == 6
    assert local_date.year == 2020


def test_get_12_week_bookends():
    my_date = datetime(2020, 6, 17)
    start_date_day_before, start_historic_week, start_current_week = charting.get_12_week_bookends(my_date)
    assert start_current_week.day == 15
    assert start_current_week.month == 6
    assert start_current_week.year == 2020

    assert start_historic_week.day == 23
    assert start_historic_week.month == 3
    assert start_historic_week.year == 2020

    assert start_date_day_before.day == 22
    assert start_date_day_before.month == 3
    assert start_date_day_before.year == 2020


def test_get_12_week_bookends_overlap_year():
    my_date = datetime(2020, 2, 1)
    start_date_day_before, start_historic_week, start_current_week = charting.get_12_week_bookends(my_date)
    assert start_current_week.day == 27
    assert start_current_week.month == 1
    assert start_current_week.year == 2020

    assert start_historic_week.day == 4
    assert start_historic_week.month == 11
    assert start_historic_week.year == 2019

    assert start_date_day_before.day == 3
    assert start_date_day_before.month == 11
    assert start_date_day_before.year == 2019


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

    activity = Activity(id=1, type=1, title='title', duration=25, distance=10,
                        iso_timestamp='2020-06-15T21:58:33.302785-07:00')
    activity_1 = Activity(id=2, type=2, title='title', duration=32, distance=5,
                          iso_timestamp='2020-06-17T05:58:33.302785-07:00')

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
    _, start_week, end_week = charting.get_week_bookends(my_date)

    activity = Activity(id=1, type=1, title='title', duration=25, distance=10.1,
                        iso_timestamp='2020-06-15T21:58:33.302785-07:00')
    activity_1 = Activity(id=2, type=2, title='title', duration=32, distance=5.25,
                          iso_timestamp='2020-06-21T05:58:33.302785-07:00')

    activities = [activity, activity_1]

    week_duration = charting.calc_daily_duration_per_exercise_type(activities, start_week, end_week, sum_by='distance')
    assert len(week_duration) == 5
    assert len(week_duration[1]) == 7
    assert week_duration[1] == [10.1, 0, 0, 0, 0, 0, 0]
    assert week_duration[2] == [0, 0, 0, 0, 0, 0, 5.25]


def test_week_activity_null_distance_end_week():
    # has an entry on the exact last day of the week
    iso_date = '2020-06-18T21:58:33.302785-07:00'

    my_date = datetime.strptime(iso_date, '%Y-%m-%dT%H:%M:%S.%f%z').date()
    _, start_week, end_week = charting.get_week_bookends(my_date)

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
    _, start_week, end_week = charting.get_week_bookends(my_date)

    activity = Activity(id=1, type=1, title='title', duration=25, distance=10,
                        iso_timestamp='2020-06-15T21:58:33.302785-07:00')
    activity_1 = Activity(id=2, type=2, title='title', duration=32, distance=5,
                          iso_timestamp='2020-06-22T05:58:33.302785-07:00')

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
    _, start_week, end_week = charting.get_week_bookends(my_date)

    activity = Activity(id=1, type=1, title='title', duration=25, distance=10,
                        iso_timestamp='2020-06-15T04:58:33.302785+05:00')

    activities = [activity]

    week_duration = charting.calc_daily_duration_per_exercise_type(activities, start_week, end_week, sum_by='distance')
    assert len(week_duration) == 5
    assert len(week_duration[1]) == 7
    assert week_duration[1] == [10, 0, 0, 0, 0, 0, 0]


def test_calc_week_totals_by_exercise_type():
    exercise_dict = {1: [10, 0, 0, 0, 0, 0, 0],
                     2: [0, 20, 0, 0, 0, 0, 0],
                     3: [0, 0, 30, 0, 0, 0, 0],
                     4: [0, 0, 10, 40, 0, 0, 0],
                     5: [0, 0, 0, 0, 50, 0, 0],
                     6: [0, 0, 0, 0, 0, 60, 0],
                     }

    activities_grand_total, dict_counts, grand_total, dict_totals = charting.calc_week_totals_by_exercise_type(
        exercise_dict)

    assert activities_grand_total == 7
    assert grand_total == 220
    assert dict_counts == {1: 1, 2: 1, 3: 1, 4: 2, 5: 1, 6: 1}
    assert dict_totals == {1: 10, 2: 20, 3: 30, 4: 50, 5: 50, 6: 60}


def test_calc_week_totals_by_exercise_type_floats():
    exercise_dict = {1: [10.1, 0, 10.1, 0, 0, 0, 0],
                     2: [0, 20.2, 0, 0, 0, 0, 0],
                     3: [0, 0, 0, 0, 0, 0, 0],
                     4: [0, 0, 0, 0, 0, 0, 0],
                     5: [0, 0, 0, 0, 0, 0, 0],
                     6: [0, 0, 0, 0, 0, 0, 0],
                     }

    activities_grand_total, dict_counts, grand_total, dict_totals = charting.calc_week_totals_by_exercise_type(
        exercise_dict)

    assert activities_grand_total == 3
    assert grand_total == 40.4
    assert dict_counts == {1: 2, 2: 1, 3: 0, 4: 0, 5: 0, 6: 0}
    assert dict_totals == {1: 20.2, 2: 20.2, 3: 0, 4: 0, 5: 0, 6: 0}


def test_calc_weekly_totals():
    iso_date = '2020-06-18T21:58:33.302785-07:00'

    my_date = datetime.strptime(iso_date, '%Y-%m-%dT%H:%M:%S.%f%z').date()
    _, start_week, _ = charting.get_week_bookends(my_date)

    activities = [Activity(id=1, type=1, title='title', duration=20,
                           iso_timestamp='2020-06-16T04:58:33.302785+05:00'),
                  Activity(id=2, type=4, title='title', distance=10, duration=15,
                           iso_timestamp='2020-06-17T04:58:33.302785+05:00'),
                  Activity(id=3, type=1, title='title', duration=34,
                           iso_timestamp='2020-06-18T04:58:33.302785+05:00'),
                  Activity(id=4, type=3, title='title', duration=25,
                           iso_timestamp='2020-06-19T04:58:33.302785+05:00')
                  ]

    total_count_all_activities, total_count_by_exercise_type, \
    total_duration_all_activities, total_duration_by_exercise_type, \
    total_distance_all_activities, total_distance_by_exercise_type = \
        charting.calc_weekly_totals(activities, start_week)

    assert total_count_all_activities == 4
    assert total_count_by_exercise_type == {1: 2, 2: 0, 3: 1, 4: 1, 5: 0}
    assert total_duration_all_activities == 94
    assert total_distance_all_activities == 10
    assert total_duration_by_exercise_type == {1: 54, 2: 0, 3: 25, 4: 15, 5: 0}
    assert total_distance_by_exercise_type == {1: 0, 2: 0, 3: 0, 4: 10, 5: 0}


weekly_totals_test_data = [([Goal(title="My Exercise",
                                  motivation="Why am i motivated to do this",
                                  acceptance_criteria="My acceptance criteria",
                                  reward="how will i reward myself",
                                  frequency=5,
                                  frequency_activity_type=-1,
                                  user_id=1)],
                            [Activity(id=1, type=1, title='title', duration=20,
                                      iso_timestamp='2020-06-16T04:58:33.302785+05:00')],
                            [(20, 0, 0)]),
                           ([Goal(title="My Exercise",
                                  motivation="Why am i motivated to do this",
                                  acceptance_criteria="My acceptance criteria",
                                  reward="how will i reward myself",
                                  frequency=5,
                                  frequency_activity_type=3,
                                  user_id=1)],
                            [Activity(id=1, type=3, title='title', duration=20,
                                      iso_timestamp='2020-06-16T04:58:33.302785+05:00')],
                            [(20, 0, 0)]),
                           ([Goal(title="My Exercise",
                                  motivation="Why am i motivated to do this",
                                  acceptance_criteria="My acceptance criteria",
                                  reward="how will i reward myself",
                                  frequency=5,
                                  frequency_activity_type=3,
                                  user_id=1)],
                            [Activity(id=1, type=3, title='title', duration=20,
                                      iso_timestamp='2020-06-16T04:58:33.302785+05:00'),
                             Activity(id=1, type=3, title='title', duration=20,
                                      iso_timestamp='2020-06-17T04:58:33.302785+05:00')
                             ],
                            [(40, 0, 0)]),
                           ([Goal(title="My Exercise",
                                  motivation="Why am i motivated to do this",
                                  acceptance_criteria="My acceptance criteria",
                                  reward="how will i reward myself",
                                  duration=60,
                                  duration_activity_type=-1,
                                  user_id=1)],
                            [Activity(id=1, type=3, title='title', duration=20,
                                      iso_timestamp='2020-06-16T04:58:33.302785+05:00')],
                            [(0, 33, 0)]),
                           ([Goal(title="My Exercise",
                                  motivation="Why am i motivated to do this",
                                  acceptance_criteria="My acceptance criteria",
                                  reward="how will i reward myself",
                                  duration=60,
                                  duration_activity_type=4,
                                  user_id=1)],
                            [Activity(id=1, type=4, title='title', duration=20,
                                      iso_timestamp='2020-06-16T04:58:33.302785+05:00')],
                            [(0, 33, 0)]),
                           ([Goal(title="My Exercise",
                                  motivation="Why am i motivated to do this",
                                  acceptance_criteria="My acceptance criteria",
                                  reward="how will i reward myself",
                                  distance=60,
                                  distance_activity_type=-1,
                                  user_id=1)],
                            [Activity(id=1, type=3, title='title', distance=20,
                                      iso_timestamp='2020-06-16T04:58:33.302785+05:00')],
                            [(0, 0, 33)]),
                           ([Goal(title="My Exercise",
                                  motivation="Why am i motivated to do this",
                                  acceptance_criteria="My acceptance criteria",
                                  reward="how will i reward myself",
                                  distance=60,
                                  distance_activity_type=4,
                                  user_id=1)],
                            [Activity(id=1, type=4, title='title', distance=20,
                                      iso_timestamp='2020-06-16T04:58:33.302785+05:00')],
                            [(0, 0, 33)]),
                           ([Goal(title="My Exercise",
                                  motivation="Why am i motivated to do this",
                                  acceptance_criteria="My acceptance criteria",
                                  reward="how will i reward myself",
                                  distance=60,
                                  distance_activity_type=4,
                                  user_id=1),
                             Goal(title="My Exercise",
                                  motivation="Why am i motivated to do this",
                                  acceptance_criteria="My acceptance criteria",
                                  reward="how will i reward myself",
                                  duration=60,
                                  duration_activity_type=-1,
                                  user_id=1)
                             ],
                            [Activity(id=1, type=4, title='title', distance=20, duration=20,
                                      iso_timestamp='2020-06-16T04:58:33.302785+05:00'),
                             Activity(id=1, type=2, title='title', duration=20,
                                      iso_timestamp='2020-06-17T04:58:33.302785+05:00')
                             ],
                            [(0, 0, 33), (0, 66, 0)]),
                           ([Goal(title="My Exercise",
                                  motivation="Why am i motivated to do this",
                                  acceptance_criteria="My acceptance criteria",
                                  reward="how will i reward myself",
                                  frequency=3,
                                  frequency_activity_type=-1,
                                  duration=60,
                                  duration_activity_type=3,
                                  distance=60,
                                  distance_activity_type=4,
                                  user_id=1),
                             ],
                            [Activity(id=1, type=4, title='title', distance=20, duration=20,
                                      iso_timestamp='2020-06-16T04:58:33.302785+05:00'),
                             Activity(id=1, type=4, title='title', duration=20,
                                      iso_timestamp='2020-06-17T04:58:33.302785+05:00'),
                             Activity(id=1, type=2, title='title', duration=10,
                                      iso_timestamp='2020-06-17T04:58:33.302785+05:00')],
                            [(100, 0, 33)])
                           ]


@pytest.mark.parametrize("goals,activities,expected_percentages", weekly_totals_test_data)
def test_compare_weekly_totals_to_goals_params(goals, activities, expected_percentages):
    iso_date = '2020-06-18T21:58:33.302785-07:00'

    my_date = datetime.strptime(iso_date, '%Y-%m-%dT%H:%M:%S.%f%z').date()
    _, start_week, _ = charting.get_week_bookends(my_date)

    percentages = charting.compare_weekly_totals_to_goals(goals, activities, start_week)
    assert percentages == expected_percentages
