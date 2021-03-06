
cwd:= $(shell pwd)

MODULE := logmyexercise.py
MY_SECRET := $(shell python -c 'import os; print(os.urandom(16))')

BLUE='\033[0;34m'
NC='\033[0m' # No Color

# This version-strategy uses git tags to set the version string
TAG := $(shell git describe --tags --always --dirty)

run:
	@flask run

test:
# pytest is not generating coverage data files for some reason
# using coverage directly
#	@pytest
	@coverage run -m pytest 
	@coverage xml

lint:
	@echo "\n${BLUE}Running Pylint against source and test files...${NC}\n"
	@pylint --rcfile=setup.cfg app
	@echo "\n${BLUE}Running Flake8 against source and test files...${NC}\n"
	@flake8
	@echo "\n${BLUE}Running Bandit against source files...${NC}\n"
	@bandit -r --ini setup.cfg

sonar:
	@sonar-scanner

version:
	@echo $(TAG)

.PHONY: clean test

clean:
	@echo "removing old files"
	@rm -rf .pytest_cache __pycache__ tests/__pycache__ .coverage tests/.pytest_cache
	@rm -f coverage.xml

deploy:
# sets the environment variables, upgrades the database and then deploys the code
# currently uses the staging configuration inside config.py on EB
# this controls the database to use
	@echo "Deploying to EB"
	# FLASK_CONFIG = 'staging'
	#@eb setenv  CALL_STRAVA_API=$(CALL_STRAVA_API)  STRAVA_CLIENT_SECRET=$(STRAVA_CLIENT_SECRET)\
	 			STRAVA_CLIENT_ID=$(STRAVA_CLIENT_ID) STRAVA_CLIENT_DOMAIN=$(STRAVA_CLIENT_DOMAIN)\
	 			FLASK_APP=$(MODULE) FLASK_CONFIG=$(FLASK_CONFIG) AUTH0_CLIENT_ID=$(AUTH0_CLIENT_ID)\
	 			AUTH0_CLIENT_SECRET=$(AUTH0_CLIENT_SECRET) AUTH0_CLIENT_DOMAIN=$(AUTH0_CLIENT_DOMAIN)\
	 			FLASK_SECRET_KEY=$(MY_SECRET) STAGING_DATABASE_URL=$(STAGING_DATABASE_URL)\
	 			STRAVA_VERIFY_TOKEN=$(STRAVA_VERIFY_TOKEN) STRAVA_SUBSCRIPTION_ID=$(STRAVA_SUBSCRIPTION_ID)\
	 			S3_BUCKET=$(S3_BUCKET) CONTACT_US_FORMAT = $(CONTACT_US_FORMAT)

	@eb deploy
	@eb open




