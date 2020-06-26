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


def get_12_week_bookends(input_date: datetime) -> (date, date, date):
    """
    Calculates a 12 week window using the input_date as a start point.
    Calculates the date for the Monday of the current week,
    the Monday of the week 12 weeks prior
    the Sunday of the week 12 weeks prior

    :param input_date: current date to base calculations off
    :type input_date: date
    :return: (start_historic_week_date_day_before, start_historic_week_date, start_current_week_date)
    :rtype: a tuple of dates
    """
    start_current_week_date = get_start_week_date(input_date, 0)
    start_historic_week_date = get_start_week_date(input_date, 12)
    start_historic_week_date_day_before = start_historic_week_date + timedelta(days=-1)
    return start_historic_week_date_day_before, start_historic_week_date, start_current_week_date


def get_date_from_isotimestamp(iso_timestamp, timestamp):
    """
    Returns a date based on the provided iso_timestamp
    :param iso_timestamp: timestamp to convert to date
    :type iso_timestamp: string
    :param timestamp: the timestamp in UTC time
    :type timestamp: date
    :return: iso_timestamp as a date
    :rtype: date
    """
    if iso_timestamp:
        local_date = datetime.strptime(iso_timestamp, '%Y-%m-%dT%H:%M:%S.%f%z').date()
    else:
        # if the local time as a iso string isn't available use the timestamp and assume UTC
        my_utc = timezone('UTC')
        local_date = my_utc.localize(timestamp).date()

    return local_date


def determine_value_to_add(activity, local_date: date, start_date: date, end_date: date = None,
                           sum_by: str = 'duration'):
    """
    Determines whether the activity falls in the date range indicated by [start_date, end_date].
    If it does, then determines how much activity to count and whether it is duration or distance being measured.

    :param activity: activity taken place
    :type activity: activity
    :param local_date: the date the activity took place in local time, could be different to the UTC date
    :type local_date: date
    :param start_date: the start of the time period in consideration
    :type start_date: date
    :param end_date: the end of the time period in consideration
    :type end_date: date
    :param sum_by: whether to sum by distance or duration
    :type sum_by: string
    :return: a tuple where first value is whether activity should be added, second is the value to be added
    :rtype: a tuple (boolean, int)
    """
    to_add = 0
    if sum_by == 'duration':
        to_add = activity.duration if activity.duration else 0
    elif activity.distance:
        to_add = round(float(activity.distance), 2)

    add_it = False
    if not end_date:
        if local_date >= start_date:
            add_it = True
    elif start_date <= local_date <= end_date:
        add_it = True

    return add_it, to_add


def calc_daily_duration_per_exercise_type(activities, start_date: date, end_date: date = None,
                                          sum_by: str = 'duration'):
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
        local_date = get_date_from_isotimestamp(activity.iso_timestamp, activity.timestamp)

        # add up the data, determine what to add by and whether the localised date is in the date range
        add_it, to_add = determine_value_to_add(activity, local_date, start_date, end_date, sum_by)

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
    :param sum_by: whether to sum by duration or distance
    :type activities: string
    :return: a list of dicts where the keys are label, backgroundColor, data
    :rtype: a list
    """
    exercise_dict = calc_daily_duration_per_exercise_type(activities, start_date, end_date, sum_by)
    display_data = []
    for key in sorted(exercise_dict):
        if sum(exercise_dict[key]) > 0:
            # need to display this on the chart
            display_data.append({'label': ACTIVITIES_LOOKUP[key],
                                 'backgroundColor': ACTIVITY_COLOR_LOOKUP[key],
                                 'data': exercise_dict[key]})

    return display_data


def calc_week_totals_by_exercise_type(exercise_dict):
    """
    calculates the total number of exercises performed irrespective of exercise_type in a week,
    the total number for each exercise_type in a week and the total weekly minutes/kms per exercise_type
    total
    :param exercise_dict:a dictionary where key is exerise_type and value is a list
    representing minutes/kms spent on that exercise_type on that day
    :type exercise_dict:
    :return: total number of activities performed in the week, a dict with total number of activities per activity type,
    total minutes/kms across all activities
    a dict with key the activity_type and value is total minutes/kms spent on that activity_type
    :rtype: tuple with 4 items
    """
    dict_totals = {}
    grand_total = float(0.0)
    activities_grand_total = 0
    dict_number_activities = {}
    for exercise_type, days in exercise_dict.items():
        dict_totals[exercise_type] = sum(days)
        grand_total += sum(days)
        number_activities = sum(1 if daily_total > 0 else 0 for daily_total in days)
        activities_grand_total += number_activities
        dict_number_activities[exercise_type] = number_activities

    return activities_grand_total, dict_number_activities, grand_total, dict_totals


def calc_weekly_totals(activities, start_date: date, end_date: date = None):
    """
    Calculates the weekly grand totals for duration and distance and number of exercises performed
    :param activities: list of activities to count
    :type activities: activity
    :param start_date: the start date of the week
    :type start_date: Date
    :param end_date: the end date of the week
    :type end_date: Date
    :return: total count of activities in the week, total count of activities by exercise_type,
    weekly total of exercise duration,
    weekly total of exercise duration by exercise_type,
    weekly total of exercise distance, weekly total of exercise distance by exercise_type,
    :rtype: a tuple with 6 elements
    """
    dict_by_duration = calc_daily_duration_per_exercise_type(activities, start_date, end_date, 'duration')
    dict_by_distance = calc_daily_duration_per_exercise_type(activities, start_date, end_date, 'distance')

    total_count_all_activities, total_count_by_exercise_type, total_duration_all_activities, \
        total_duration_by_exercise_type = calc_week_totals_by_exercise_type(dict_by_duration)
    _, _, total_distance_all_activities, total_distance_by_exercise_type = calc_week_totals_by_exercise_type(
        dict_by_distance)

    return total_count_all_activities, total_count_by_exercise_type, total_duration_all_activities, \
        total_duration_by_exercise_type, total_distance_all_activities, total_distance_by_exercise_type


def compare_weekly_totals_to_goals(goals, activities, start_date: date, end_date: date = None):
    """
    Compares the weekly frequency, duration, distance figrues against goals in order to calculate %age of the goal
    :param goals: a list of user Goal
    :type goals: List
    :param total_count_all_activities: total number of activities in the week
    :type total_count_all_activities: int
    :param total_count_by_exercise_type: total number of activities per activity type
    :type total_count_by_exercise_type: Dict
    :param total_duration_all_activities: total duration of activities in the week
    :type total_duration_all_activities: float
    :param total_duration_by_exercise_type: total duration per activity type
    :type total_duration_by_exercise_type: dict
    :param total_distance_all_activities: total distance o activities in the week
    :type total_distance_all_activities: float
    :param total_distance_by_exercise_type: total distance of activities per activity type
    :type total_distance_by_exercise_type: dict
    :return: A list of tuples where each tuple contains (%age met of total activities goal,
    %age met of total duration goal, %age met of total distance goal)
    :rtype: tuple
    """
    total_count_all_activities, total_count_by_exercise_type, \
        total_duration_all_activities, total_duration_by_exercise_type, \
        total_distance_all_activities, total_distance_by_exercise_type = \
        calc_weekly_totals(activities, start_date, end_date)

    percentages = []
    for goal in goals:
        frequency_percentage, duration_percentage, distance_percentage = 0, 0, 0

        if goal.frequency:
            # look to see if across all activities or specific activity type
            if goal.frequency_activity_type == -1:
                numerator = total_count_all_activities
            else:
                numerator = total_count_by_exercise_type[goal.frequency_activity_type]
            frequency_percentage = int(numerator / goal.frequency * 100)

        if goal.duration:
            if goal.duration_activity_type == -1:
                numerator = total_duration_all_activities
            else:
                numerator = total_duration_by_exercise_type[goal.duration_activity_type]
            duration_percentage = int(numerator / goal.duration * 100)

        if goal.distance:
            if goal.distance_activity_type == -1:
                numerator = total_distance_all_activities
            else:
                numerator = total_distance_by_exercise_type[goal.distance_activity_type]
            distance_percentage = int(numerator / goal.distance * 100)

        percentages.append((frequency_percentage, duration_percentage, distance_percentage))

    return percentages
