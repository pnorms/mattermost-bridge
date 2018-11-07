FROM python:3

ADD tower.py /
ADD config.json /

RUN pip install flask
RUN pip install requests

CMD [ "python", "./tower.py" ]
