from flask import url_for
from flask_testing import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.support.ui import Select

from app import create_app, db
from app.models import User

test_user_username = "my_test_user"
test_user_email = "test@test.email"
test_user_password = "test_pwd"


class TestBase(LiveServerTestCase):

    def create_app(self):
        app = create_app('testing')
        return app

    def setUp(self):
        """Setup the test driver and create test users"""
        self.driver = webdriver.Chrome()
        self.driver.get(self.get_server_url())

        db.drop_all()
        db.create_all()

        user = User(username=test_user_username, email=test_user_email)
        user.set_password(test_user_password)
        db.session.add(user)
        db.session.commit()

    def tearDown(self):
        self.driver.quit()


class TestLogin(TestBase):

    def test_login_ok(self):
        # Fill in login form
        self.driver.get(self.get_server_url() + "/auth/login")
        self.driver.find_element_by_id("username").send_keys(test_user_username)
        self.driver.find_element_by_id("password").send_keys(
            test_user_password)
        self.driver.find_element_by_id("submit").click()

        # Assert that username is shown
        username_navbar = self.driver.find_element_by_id(
            "navbarDropdownMenuLink").text
        assert test_user_username in username_navbar

        # no activities should be shown
        no_activity_msg = self.driver.find_element_by_id("no_reg").text
        assert "No regular activities" in no_activity_msg

        # try and access the login page, should remain on the index page as now logged in
        self.driver.get(self.get_server_url() + "/auth/login")
        no_activity_msg = self.driver.find_element_by_id("no_reg").text
        assert "No regular activities" in no_activity_msg


class TestActivity(TestBase):

    def login_user(self):
        self.driver.get(self.get_server_url() + "/auth/login")
        self.driver.find_element_by_id("username").send_keys(test_user_username)
        self.driver.find_element_by_id("password").send_keys(
            test_user_password)
        self.driver.find_element_by_id("submit").click()
        self.driver.find_element_by_id("set_up").click()

    def test_create_regular_activity_ok(self):
        self.login_user()

        assert url_for('main.add_regular_activity') in self.driver.current_url

        select = Select(self.driver.find_element_by_id("activity_type"))
        select.select_by_visible_text('Yoga')
        self.driver.find_element_by_id("title").send_keys(
            "title of workout")
        self.driver.find_element_by_id("description").send_keys(
            "a description")
        self.driver.find_element_by_id("duration").send_keys(
            "10")
        self.driver.find_element_by_id("submit").click()

        assert url_for('main.regular_activities') in self.driver.current_url

        # Assert success message is shown
        success_message = self.driver.find_element_by_class_name("alert-success").text
        assert "Your regular activity is recorded" in success_message

        # check the table is showing the data correctly
        # should be a header row and then a data row with the activity data
        table = self.driver.find_element_by_id("activity_list")
        rows = table.find_elements_by_tag_name("tr")

        self.assertEqual(len(rows), 2)
        cols = rows[1].find_elements_by_tag_name("td")
        self.assertEqual(len(cols), 6)

        self.assertEqual(cols[1].text, "title of workout")
        self.assertEqual(cols[2].text, "10")
        self.assertEqual(cols[3].text, "")
        self.assertEqual(cols[4].text, "a description")

        self.driver.find_element_by_id("edit_activity_link").click()
        # check the fields are showing the same values as those initially input
        select = Select(self.driver.find_element_by_id("activity_type"))
        self.assertEqual(select.first_selected_option.text, "Yoga")
        self.assertEqual(self.driver.find_element_by_id("title").get_attribute('value'), "title of workout")
        self.assertEqual(self.driver.find_element_by_id("description").get_attribute('value'), "a description")
        self.assertEqual(self.driver.find_element_by_id("duration").get_attribute('value'), "10")

    def test_create_regular_activity_missing_fields(self):
        self.login_user()

        # title is mandatory
        self.driver.find_element_by_id("description").send_keys(
            "a description")
        self.driver.find_element_by_id("duration").send_keys(
            "10")
        self.driver.find_element_by_id("submit").click()

        # Error message is shown
        error_message = self.driver.find_element_by_class_name("text-muted").text
        assert "This field is required" in error_message

        # duration is mandatory
        self.driver.find_element_by_id("title").send_keys(
            "a title")
        self.driver.find_element_by_id("description").send_keys(
            "a description")
        self.driver.find_element_by_id("duration").clear()
        self.driver.find_element_by_id("submit").click()

        # duration cannot be bigger than 999
        self.driver.find_element_by_id("title").send_keys(
            "a title")
        self.driver.find_element_by_id("description").send_keys(
            "a description")
        self.driver.find_element_by_id("duration").clear()
        self.driver.find_element_by_id("duration").send_keys("1000")
        self.driver.find_element_by_id("submit").click()

        # Error message is shown
        error_message = self.driver.find_element_by_class_name("text-muted").text
        assert "Please enter a number between 0 and 999" in error_message

    def test_edit_regular_activity(self):
        # create an activity and then edit it
        self.login_user()

        self.driver.find_element_by_id("title").send_keys(
            "title of workout")
        self.driver.find_element_by_id("description").send_keys(
            "a description")
        self.driver.find_element_by_id("duration").send_keys(
            "10")
        self.driver.find_element_by_id("submit").click()

        self.driver.find_element_by_id("edit_activity_link").click()

        self.driver.find_element_by_id("title").send_keys(
            "title of workout12 ")
        self.driver.find_element_by_id("description").send_keys(
            "a description 12")
        self.driver.find_element_by_id("duration").clear()
        self.driver.find_element_by_id("duration").send_keys(
            "100")
        self.driver.find_element_by_id("submit").click()

        assert url_for('main.regular_activities') in self.driver.current_url

        # Assert success message is shown
        success_message = self.driver.find_element_by_class_name("alert-success").text
        assert "Saved changes" in success_message

    def test_delete_regular_activity(self):
        # login, create an activity and then delete it

        self.login_user()

        self.driver.find_element_by_id("title").send_keys(
            "title of workout")
        self.driver.find_element_by_id("description").send_keys(
            "a description")
        self.driver.find_element_by_id("duration").send_keys(
            "10")
        self.driver.find_element_by_id("submit").click()

        self.driver.find_element_by_id("delete_activity_link").click()

        # Assert success message is shown
        success_message = self.driver.find_element_by_class_name("alert-success").text
        assert "Deleted" in success_message

    def test_log_activity(self):
        # create an activity and log it being completed
        self.login_user()

        self.driver.find_element_by_id("title").send_keys(
            "title of workout")
        self.driver.find_element_by_id("description").send_keys(
            "a description")
        self.driver.find_element_by_id("duration").send_keys(
            "10")

        self.driver.find_element_by_id("submit").click()
        self.driver.find_element_by_id("home_link").click()

        # check timezone info has been added to the URL
        assert "?tz=" in self.driver.find_element_by_class_name("stretched-link").get_attribute("href")
        self.driver.find_element_by_class_name("stretched-link").click()

        success_message = self.driver.find_element_by_class_name("alert-success").text
        assert "Well done on completing" in success_message

        self.driver.find_element_by_id('my_log_link').click()
        table = self.driver.find_element_by_id("activity_list")
        rows = table.find_elements_by_tag_name("tr")

        assert len(rows) == 2
        cols = rows[1].find_elements_by_tag_name("td")
        assert len(cols) == 6

        assert cols[2].text == "title of workout"
        assert cols[3].text == "10"

    def test_log_unique_activity(self):
        # log a one-off activity on the home page
        self.login_user()

        self.driver.find_element_by_id("home_link").click()

        self.driver.find_element_by_id("title").send_keys(
            "title of workout")
        self.driver.find_element_by_id("description").send_keys(
            "a description")
        self.driver.find_element_by_id("duration").send_keys(
            "65")
        self.driver.find_element_by_id("distance").send_keys(
            "10")
        self.driver.find_element_by_id("save_exercise").click()

        success_message = self.driver.find_element_by_class_name("alert-success").text
        assert "Well done on completing" in success_message

        self.driver.find_element_by_id('my_log_link').click()
        table = self.driver.find_element_by_id("activity_list")
        rows = table.find_elements_by_tag_name("tr")

        assert len(rows) == 2
        cols = rows[1].find_elements_by_tag_name("td")
        assert len(cols) == 6

        assert cols[2].text == "title of workout"
        assert cols[3].text == "65"
        assert cols[4].text == "10.00"
