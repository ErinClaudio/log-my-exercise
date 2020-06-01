# log-my-exercise
This application is a simple web-based exercise tracker. It enables users to log exercises, view history and also has Strava integration.

# Motivation
I decided to build this app for a couple of reasons:
* Most exercise tracking apps are complicated and tie you to a particular company or ecosystem
* I wanted an easy way to log a repetitive workout that I perform multiple times a week into Strave. I wanted this to be a one-click input. Manual data input into Strava is painful especially when it's the same data input each exercise.

# Status
The app is working and contains the initial features I was interested in.

# Screenshots
To be added

# Technology
It's built in Python leveraging the Flask framework. Database access is performed via SQLAlchemy.
I've been using Python 3.7.7 and have tested it under Chrome, Brave and Safari on a Mac.
It requires a database backend. For development, I've been using sqlite and I've tested it under MySQL.
The Auth0 website is used for authentication. I use the Authlib package to assist with the authentication.
Strava APIs are used for integration with Strava.

The requirements.txt file has further information on the dependent packages

# Features
This app contains the following features:
* ability to create a regular exercise routine which you'd perform repeatedly e.g. a YouTube workout
* log that you've performed this exercise
* view a history of all activities performed
* enables a user to give permission to upload their exercises to Strava
* send the exercise to Strava
* authenticate users using the Auth0 website

# Installation
It's a standard Flask app with a database backend. To install and run locally:
* Ensure Python is installed. It's been tested with Python 3.7.7
* Fork this repo
* Register an app with Auth0
* Register an app with Strava if you'd like Strava integration
* Set-up the required environment variables on your machine or server. These are listed in the config.py file. These are used to manage secrets and other runtime configurations.
* Install the necessary Python packages described in requirements.txt. Best if you create a virtual environment and activate it.
* The environment variable FLASK_CONFIG controls which configiration in config.py will be used.
* Install the database tables. This can be done via `flask db upgrade`. It's dependent on the environment variables used to store the path to the database being configured correctly.
* To run, execute `flask run` and you should see flask starting and giving the URL to access

# Tests
The tests folder contains some tests. These are not complete and require enhancements.
To run them execute `Make test` on the command line.
You can also run various linters by entering `Make lint`. These will provide some errors due to the way Flask works.

# How to use?
You can take this code and run on a server via mechanisms such as Docker or AWS Elastic Beanstalk.

# Contribute
Feedback and contributions are welcome. 

# To dos
* Improve the tests by introducing mocks
* Improve the UI
* Ability for a user to disable the Strava integration
* Callback for Strava to disable the Strava integration for a user. Required to make this productionised with Strava.

# License
This is licensed under an Apache licence

