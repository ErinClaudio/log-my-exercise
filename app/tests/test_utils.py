import json
import glob
import os


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
