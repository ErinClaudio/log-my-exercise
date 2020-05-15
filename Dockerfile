FROM tiangolo/meinheld-gunicorn-flask:python3.7

COPY requirements.txt /tmp/
RUN pip install -U pip
RUN pip install -r /tmp/requirements.txt

ENV MODULE_NAME logmyexercise

COPY app app
COPY migrations migrations
COPY logmyexercise.py config.py app.db ./

