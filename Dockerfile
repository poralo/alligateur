FROM python:3.7

RUN adduser --disabled-password microblog

WORKDIR /home/

COPY aggregator aggregator
WORKDIR /home/aggregator
RUN python -m venv venv
RUN venv/bin/pip install wheel
RUN venv/bin/pip install -r requirements.txt

RUN venv/bin/python utils/create_table.py

EXPOSE 5000

CMD ["aggregator.py"]
ENTRYPOINT ["venv/bin/python"]

