from datetime import datetime
import os
import json

import pytz
import uuid

from app.services import aws


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

    return datetime.now(local_tz).isoformat()


def generate_random_filename_from_email(email):
    """
    returns a filename with some random characters infront of part of the email
    the part of the email prior to the @ is used to generate the filename
    :param email: email address
    :type email:
    :return: the filename
    :rtype:
    """
    email_prefix = email[:email.index("@")]
    random_file_name = ''.join([str(uuid.uuid4().hex[:6]), email_prefix, '.json'])

    return random_file_name


def save_contents_file(email, contents):
    """
    Saves the received feedback to a file.
    This will be on S3 or the local filesystem dependent on the environment property
    CONTACT_US_FORMAT=S3, saves to S3 otherwise saves to file system
    The env variable S3_BUCKET indicates the S3 bucket to use

    :param email: email address of person providing feedback
    :type email: string
    :param contents: contents of the feedback
    :type contents: json
    :return: whether the save was a success or not
    :rtype: Boolean
    """
    filename = generate_random_filename_from_email(email)

    # check to see if to save to AWS or filesystem
    if os.getenv('CONTACT_US_FORMAT') == 'S3':
        return aws.save_s3(os.getenv('S3_BUCKET'), filename, json.dumps(contents))

    # write to file otherwise
    with open(filename, 'w') as outfile:
        json.dump(contents, outfile)
        return True
