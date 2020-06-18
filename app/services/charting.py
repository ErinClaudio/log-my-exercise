from datetime import datetime, timezone, timedelta
from pytz import timezone
import pytz

from app.main import ACTIVITIES_LOOKUP

# use this  color map to display the different types of activities
# be consistent and use for charts and for regular activities
# colors came from https://colorbrewer2.org/
# key corresponds to activity_type and value is the color hex code
ACTIVITY_COLOR_LOOKUP = {1: '#7fc97f', 2: '#beaed4', 3: '#fdc086', 4: '#ffff99', 5: '#386cb0', 6: '#f0027f'}


def get_start_week_date(input_date):
    """
    calculates the date at the start of the week based on the provided date
    :param input_date: date to base the start of week on, defaults to current date if None
    :type input_date: datetime
    :return: midnight at the date at the start of the week
    :rtype:
    """
    calc_date = input_date
    if not input_date:
        calc_date = datetime.now(timezone('UTC'))
    date_start_week = calc_date - timedelta(days=calc_date.weekday())

    return date_start_week.replace(hour=0, minute=0, second=0, microsecond=0)


def get_start_week_date_before(input_date):
    """
    calculates the date at the day before the start of the week based on the provided date
    :param input_date: date to base the start of week on, defaults to current date if None
    :type input_date: datetime
    :return: midnight at the date at the day before the start of the week
    :rtype:
    """
    calc_date = input_date
    if not input_date:
        calc_date = datetime.now(timezone('UTC'))
    date_start_week = calc_date - timedelta(days=calc_date.weekday() + 1)

    return date_start_week.replace(hour=0, minute=0, second=0, microsecond=0)


def calc_daily_duration_per_exercise_type(activities, start_date):
    """
    Given a list of activities for the last week, will put them into a dictionary of arrays.
    The key represents the activity type, the array represents the minutes spent on that activity for each day of the week
    The first item in the array represents Monday, the second is Tuesday and so on
    It assumes the activities only go back since the start of the calendar week of today's date

    :param activities: a list of Activity
    :type activities: a list of Activity objects
    :return: a dictionary with the key representing the activity type and an array representing minutes of that activity
    performed each day of the week (7 entries)
    :rtype: Dictionary
    """
    exercise_dict = {1: [0, 0, 0, 0, 0, 0, 0], 2: [0, 0, 0, 0, 0, 0, 0], 3: [0, 0, 0, 0, 0, 0, 0],
                     4: [0, 0, 0, 0, 0, 0, 0], 5: [0, 0, 0, 0, 0, 0, 0]}

    # need to consider this in local time to the user, not UTC time
    for activity in activities:
        if activity.iso_timestamp:
            local_date = datetime.strptime(activity.iso_timestamp, '%Y-%m-%dT%H:%M:%S.%f%z')
        else:
            # if the local time as a iso string isn't available use the timestamp and assume UTC
            my_utc = timezone('UTC')
            local_date = my_utc.localize(activity.timestamp)

        if local_date >= start_date:
            exercise_dict[activity.type][local_date.weekday()] += activity.duration


    return exercise_dict


def get_chart_dataset(activities, start_date):
    """
    returns an array of tuples with each tuple representing a data set to
    be visualised in chart.js
    ignores any exercise types where that exercise does not occur in the provided activities
    :param activities: a list of Activity
    :type activities: a list of Activity objects
    :return: a list of dicts where the keys are label, backgroundColor, data
    :rtype: a list
    """
    exercise_dict = calc_daily_duration_per_exercise_type(activities, start_date)
    display_data = []
    for key in sorted(exercise_dict):
        if sum(exercise_dict[key]) > 0:
            # need to display this on the chart
            display_data.append({'label': ACTIVITIES_LOOKUP[key],
                                 'backgroundColor': ACTIVITY_COLOR_LOOKUP[key],
                                 'data': exercise_dict[key]})

    return display_data
