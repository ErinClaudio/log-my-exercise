from datetime import datetime, timedelta, date

from pytz import timezone

from app.main import ACTIVITIES_LOOKUP

# use this  color map to display the different types of activities
# be consistent and use for charts and for regular activities
# colors came from https://colorbrewer2.org/
# key corresponds to activity_type and value is the color hex code
ACTIVITY_COLOR_LOOKUP = {1: '#7fc97f', 2: '#beaed4', 3: '#fdc086', 4: '#ffff99', 5: '#386cb0', 6: '#f0027f'}


def get_start_week_date(input_date: datetime, week_offset: int = 0) -> date:
    """
    calculates the date at the start of the week based on the provided date
    :param input_date: date to base the start of week on, defaults to current date if None
    :type input_date: datetime
    :param week_offset: number of weeks prior to the input_date to offset the start of week by
    :type week_offset: int
    :return: midnight at the date at the start of the week
    :rtype:
    """
    calc_date = input_date
    if not input_date:
        calc_date = datetime.now(timezone('UTC')).date()
    date_start_week = calc_date - timedelta(days=calc_date.weekday() + (7 * week_offset))

    return date_start_week


def get_start_week_date_before(input_date: datetime, week_offset: int = 0) -> date:
    """
    calculates the date at the day before the start of the week based on the provided date
    :param input_date: date to base the start of week on, defaults to current date if None
    :type input_date: datetime
    :param week_offset: number of weeks prior to the input_date to offset the start of week by
    :type week_offset: int
    :return: midnight at the date at the day before the start of the week
    :rtype:
    """

    date_start_week = get_start_week_date(input_date, week_offset) - timedelta(days=1)

    return date_start_week


def get_week_bookends(input_date: datetime, week_offset: int = 0) -> (date, date, date):
    """
    returns a tuple representing the start of the week -1, start of week and end of week
    :param input_date: the date used to determine the start and end of the week
    :type input_date:
    :param week_offset: number of weeks prior to the input_date to offset the start of week by
    :type week_offset: int
    :return: (start_date-1, start_date, end date) all in UTC timezone with hour, minutes
    seconds, microseconds set to midnight (start of week dates) or just before midnight (end date)
    :rtype: a tuple of dates (start_date-1, start_date, end date)
    """

    date_start_week = get_start_week_date(input_date, week_offset)
    date_start_week_day_before = get_start_week_date_before(input_date, week_offset)
    date_end_week = date_start_week + timedelta(days=6)
    return (date_start_week_day_before,
            date_start_week,
            date_end_week)


def calc_daily_duration_per_exercise_type(activities, start_date: date, end_date: date = None, sum_by: str ='duration'):
    """
    Given a list of activities for the last week, will put them into a dictionary of arrays.
    The key represents the activity type, the array represents the minutes spent on that activity
    for each day of the week
    The first item in the array represents Monday, the second is Tuesday and so on
    It assumes the activities only go back since the start of the calendar week of today's date

    :param activities: a list of Activity
    :type activities: a list of Activity objects
    :param start_date: Monday's UTC date and midnight time
    :type start_date: a UTC date
    :param end_date: Sunday's UTC date and time at the end of day, ignored if None
    :type end_date: a UTC date
    :param sum_by: whether to sum by duration or distance, defaults to duration
    :type sum_by: a String either 'duration' or 'distance'
    :return: a dictionary with the key representing the activity type and an array representing minutes of that activity
    performed each day of the week (7 entries)
    :rtype: Dictionary
    """
    exercise_dict = {1: [0, 0, 0, 0, 0, 0, 0], 2: [0, 0, 0, 0, 0, 0, 0], 3: [0, 0, 0, 0, 0, 0, 0],
                     4: [0, 0, 0, 0, 0, 0, 0], 5: [0, 0, 0, 0, 0, 0, 0]}

    # need to consider this in local time to the user, not UTC time
    for activity in activities:
        if activity.iso_timestamp:
            local_date = datetime.strptime(activity.iso_timestamp, '%Y-%m-%dT%H:%M:%S.%f%z').date()
        else:
            # if the local time as a iso string isn't available use the timestamp and assume UTC
            my_utc = timezone('UTC')
            local_date = my_utc.localize(activity.timestamp).date()

        # add up the data, determine what to add by and also to include the date
        to_add = 0
        if sum_by == 'duration':
            to_add = activity.duration
        elif activity.distance:
            to_add = int(activity.distance)
        add_it = False

        if not end_date:
            if local_date >= start_date:
                add_it = True
        elif start_date <= local_date <= end_date:
            add_it = True

        if add_it:
            exercise_dict[activity.type][local_date.weekday()] += to_add

    return exercise_dict


def get_chart_dataset(activities, start_date: date, end_date: date = None, sum_by: str = 'duration'):
    """
    returns an array of tuples with each tuple representing a data set to
    be visualised in chart.js
    ignores any exercise types where that exercise does not occur in the provided activities
    :param activities: a list of Activity
    :type activities: a list of Activity objects
    :param start_date: the start of the week date from which the Activity objects should be bucketed
    :type activities: date
    :param end_date: the end of the week date from which the Activity objects should be bucketed
    :type activities: date
    :return: a list of dicts where the keys are label, backgroundColor, data
    :rtype: a list
    """
    exercise_dict = calc_daily_duration_per_exercise_type(activities, start_date, end_date, sum_by)
    print(exercise_dict)
    display_data = []
    for key in sorted(exercise_dict):
        if sum(exercise_dict[key]) > 0:
            # need to display this on the chart
            display_data.append({'label': ACTIVITIES_LOOKUP[key],
                                 'backgroundColor': ACTIVITY_COLOR_LOOKUP[key],
                                 'data': exercise_dict[key]})

    return display_data
