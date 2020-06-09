from datetime import datetime
import pytz


def get_local_time_iso(user_tz='UTC'):
    """
    converts the current time into a time local to the user's timezone
    if the provided timezone is not valid then UTC is used
    :param user_tz: representation of the local timezone
    :type user_tz: string
    :return: current datetime formatted into a ISO string
    :rtype: string
    """
    local_tz = pytz.timezone('UTC')
    try:
        # check the timezone provided is valid
        local_tz = pytz.timezone(user_tz)
    except pytz.exceptions.UnknownTimeZoneError:
        pass

    print('local tz as iso', datetime.now(local_tz).isoformat())
    return datetime.now(local_tz).isoformat()
