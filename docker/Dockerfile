FROM python:3

ADD base.py /
ADD bitbucket.py /
ADD common.py /
ADD config.json /
ADD config.py /
ADD helpers.py /
ADD tower.py /

RUN pip install flask
RUN pip install requests

COPY ca-certs/* /usr/local/share/ca-certificates/
RUN update-ca-certificates

CMD [ "python", "./base.py" ]