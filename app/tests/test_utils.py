import json
import glob
import os
from datetime import datetime


from app.services import utils


def get_tz_hour_offset(my_date):
    return int(my_date[11:13])


def test_utils_date_notz():
    iso_date = '2020-06-18T21:58:33.302785-07:00'
    my_date = datetime.strptime(iso_date, '%Y-%m-%dT%H:%M:%S.%f%z')
    current_iso_date = utils.get_iso_from_local_time(my_date)
    assert get_tz_hour_offset(current_iso_date) - my_date.hour == 0


def test_get_local_time_from_utc():
    iso_date = '2020-06-18T01:58:33'

    my_date = datetime.strptime(iso_date, '%Y-%m-%dT%H:%M:%S')
    my_date_la = utils.get_local_time_from_utc(my_date, 'America/Los_Angeles')
    assert my_date_la.day == 17
    assert my_date_la.month == 6
    assert my_date_la.minute == 58
    assert my_date_la.second == 33
    # won't assert on hour due to DST


def test_get_utc_from_local_time():
    # convert a string to a date/time that is in a local timezone and
    # check its UTC date/time is correct
    iso_date = '2020-06-18T21:58:33'

    my_date = datetime.strptime(iso_date, '%Y-%m-%dT%H:%M:%S')
    my_date_utc = utils.get_utc_from_local_time(my_date, 'America/Los_Angeles')
    assert my_date_utc.day == 19
    assert my_date_utc.month == 6
    assert my_date_utc.minute == 58
    assert my_date_utc.second == 33
    # won't assert on hour due to DST


def test_generate_random_filename_from_email():
    email = "bobby@chariot.net"
    assert "bobby" in utils.generate_random_filename_from_email(email)
    assert ".json" in utils.generate_random_filename_from_email(email)
    assert "chariot" not in utils.generate_random_filename_from_email(email)
    assert "@" not in utils.generate_random_filename_from_email(email)
    assert len(utils.generate_random_filename_from_email(email)) == 16


def test_save_contents_as_file():
    email = "bobby@chariot.net"
    json_to_save = {"id": "123456", "name": "my name"}
    utils.save_contents_file(email, json_to_save)

    # check the file exists, will need to find all files with file name containing
    # bobby
    # check there is only one
    files = glob.glob("*bobby.json")
    assert len(files) == 1
    # read in the content of this file and check it matches what was saved
    with open(files[0], 'r') as infile:
        data = infile.read()

    # parse file
    obj = json.loads(data)
    assert obj == json_to_save

    # then delete the file
    os.remove(files[0])

