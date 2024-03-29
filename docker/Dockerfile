FROM --platform=linux/amd64 python:3.10

# Run this via "build.sh" as it needs to correct build context

# Can add this line if building on internal network
# RUN echo 'Acquire::http { Proxy "http://apt-cache.reneo.io:3142"; };' > /etc/apt/apt.conf.d/01proxy

RUN apt-get update

COPY ./requirements.txt /opt/app/requirements.txt

WORKDIR /opt/app

ENV PIP_ROOT_USER_ACTION=ignore

RUN pip install gunicorn
RUN pip install -r requirements.txt

COPY docker/start-server.sh /opt/app/start-server.sh
COPY cg /opt/app/cg

WORKDIR /opt/app/cg
EXPOSE 8000
STOPSIGNAL SIGTERM

CMD ["/opt/app/start-server.sh"]
