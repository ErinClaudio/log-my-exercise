import time

from flask_testing import LiveServerTestCase
from selenium import webdriver

from flask import url_for

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

        # try and access the register page, should remain on the index page as now logged in
        self.driver.get(self.get_server_url() + "/auth/register")
        no_activity_msg = self.driver.find_element_by_id("no_reg").text
        assert "No regular activities" in no_activity_msg

    def test_login_missing_username(self):
        # Fill in login form
        self.driver.get(self.get_server_url() + "/auth/login")
        self.driver.find_element_by_id("password").send_keys(
            test_user_password)
        self.driver.find_element_by_id("submit").click()

        error_message = self.driver.find_element_by_class_name("text-muted").text
        assert "This field is required" in error_message

    def test_login_missing_password(self):
        # Fill in login form
        self.driver.get(self.get_server_url() + "/auth/login")
        self.driver.find_element_by_id("username").send_keys(
            test_user_username)
        self.driver.find_element_by_id("submit").click()

        error_message = self.driver.find_element_by_class_name("text-muted").text
        assert "This field is required" in error_message

    def test_login_invalid_password(self):
        # Fill in login form
        self.driver.get(self.get_server_url() + "/auth/login")
        self.driver.find_element_by_id("username").send_keys(
            test_user_username)
        self.driver.find_element_by_id("password").send_keys(
            test_user_password+"&&")
        self.driver.find_element_by_id("submit").click()

        error_message = self.driver.find_element_by_class_name("list-group-item").text
        assert "Invalid username or password" in error_message

    def test_login_invalid_username(self):
        # Fill in login form
        self.driver.get(self.get_server_url() + "/auth/login")
        self.driver.find_element_by_id("username").send_keys(
            test_user_username+"@£")
        self.driver.find_element_by_id("password").send_keys(
            test_user_password)
        self.driver.find_element_by_id("submit").click()

        error_message = self.driver.find_element_by_class_name("list-group-item").text
        assert "Invalid username or password" in error_message


class TestRegistration(TestBase):

    def test_registration_ok(self):
        # Click register menu link
        self.driver.get(self.get_server_url() + "/auth/register")
        # self.driver.find_element_by_id("register_link").click()

        # Fill in registration form
        self.driver.find_element_by_id("email").send_keys("test@test.com")
        self.driver.find_element_by_id("username").send_keys(
            "test")
        self.driver.find_element_by_id("password").send_keys(
            "test_password")
        self.driver.find_element_by_id("password2").send_keys(
            "test_password")
        self.driver.find_element_by_id("register").click()

        # Assert that browser redirects to login page
        assert url_for('auth.login') in self.driver.current_url

        # Assert success message is shown
        success_message = self.driver.find_element_by_class_name("list-group-item").text
        assert "Congratulations" in success_message

        # Assert that there are now 2 users in the database
        # 1 is created in the setup
        self.assertEqual(User.query.count(), 2)


    def test_registration_missing_fields(self):
        # Click register menu link
        self.driver.get(self.get_server_url() + "/auth/register")
        # self.driver.find_element_by_id("register_link").click()

        # Fill in registration form, leave out username
        self.driver.find_element_by_id("email").send_keys("test12@test.com")
        self.driver.find_element_by_id("password").send_keys(
            "test_password")
        self.driver.find_element_by_id("password2").send_keys(
            "test_password")
        self.driver.find_element_by_id("register").click()

        # Error message is shown
        error_message = self.driver.find_element_by_class_name("text-muted").text
        assert "This field is required" in error_message


    def test_registration_mismatch_password(self):
        self.driver.get(self.get_server_url() + "/auth/register")
       #  self.driver.find_element_by_id("register_link").click()

        # Fill in registration form, leave out username
        self.driver.find_element_by_id("email").send_keys("test12@test.com")
        self.driver.find_element_by_id("username").send_keys(
            "R2D2")
        self.driver.find_element_by_id("password").send_keys(
            "r2d2password")
        self.driver.find_element_by_id("password2").send_keys(
            "r2d2passwor")
        self.driver.find_element_by_id("register").click()

        # Error message is shown
        error_message = self.driver.find_element_by_tag_name("small").text
        assert "Passwords must match" in error_message

    def test_registration_duplicate_username(self):
        self.driver.get(self.get_server_url() + "/auth/register")
       # self.driver.find_element_by_id("register_link").click()

        # Fill in registration form, use same username as user already setup
        self.driver.find_element_by_id("email").send_keys("test12@test.com")
        self.driver.find_element_by_id("username").send_keys(
            test_user_username)
        self.driver.find_element_by_id("password").send_keys(
            "pwd")
        self.driver.find_element_by_id("password2").send_keys(
            "pwd")
        self.driver.find_element_by_id("register").click()

        # Error message is shown
        error_message = self.driver.find_element_by_tag_name("small").text
        assert "Please use a different username" in error_message

    def test_registration_duplicate_email(self):
        self.driver.get(self.get_server_url() + "/auth/register")
        # self.driver.find_element_by_id("register_link").click()

        # Fill in registration form, use same email as user already setup
        self.driver.find_element_by_id("email").send_keys(test_user_email)
        self.driver.find_element_by_id("username").send_keys(
            "d0")
        self.driver.find_element_by_id("password").send_keys(
            "pwd")
        self.driver.find_element_by_id("password2").send_keys(
            "pwd")
        self.driver.find_element_by_id("register").click()

        # Error message is shown
        error_message = self.driver.find_element_by_tag_name("small").text
        assert "Please use a different email" in error_message

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

        self.driver.find_element_by_id("title").send_keys(
            "title of workout")
        self.driver.find_element_by_id("description").send_keys(
            "a description")
        self.driver.find_element_by_id("duration").send_keys(
            "10")
        self.driver.find_element_by_id("submit").click()

        assert url_for('main.regular_activities') in self.driver.current_url

        # Assert success message is shown
        success_message = self.driver.find_element_by_class_name("list-group-item").text
        assert "Your regular activity is recorded" in success_message

        # check the table is showing the data correctly
        # should be a header row and then a data row with the activity data
        table = self.driver.find_element_by_id("activity_list")
        rows = table.find_elements_by_tag_name("tr")

        self.assertEqual(len(rows), 2)
        cols = rows[1].find_elements_by_tag_name("td")
        self.assertEqual(len(cols), 5)
        self.assertEqual(cols[0].text, "Workout")
        self.assertEqual(cols[1].text, "title of workout")
        self.assertEqual(cols[3].text, "a description")
        self.assertEqual(cols[2].text, "10")


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
        success_message = self.driver.find_element_by_class_name("list-group-item").text
        assert "You have successfully edited your regular activity" in success_message

    def test_delete_regular_activity(self):
        #login, create an activity and then delete it

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
        success_message = self.driver.find_element_by_class_name("list-group-item").text
        assert "You have successfully deleted the regular activity" in success_message


    def test_log_activity(self):
        #create an activity and log it being completed
        self.login_user()


        self.driver.find_element_by_id("title").send_keys(
            "title of workout")
        self.driver.find_element_by_id("description").send_keys(
            "a description")
        self.driver.find_element_by_id("duration").send_keys(
            "10")
        self.driver.find_element_by_id("submit").click()

        self.driver.find_element_by_id("home_link").click()

        self.driver.find_element_by_link_text("title of workout").click()

        success_message = self.driver.find_element_by_class_name("list-group-item").text
        assert "Well done on completing" in success_message

        self.driver.find_element_by_id('my_log_link').click()
        table = self.driver.find_element_by_id("activity_list")
        rows = table.find_elements_by_tag_name("tr")

        assert len(rows) == 2
        cols = rows[1].find_elements_by_tag_name("td")
        assert len(cols) == 4
        assert cols[1].text == "Workout"
        assert cols[2].text == "title of workout"
        assert cols[3].text == "10"
