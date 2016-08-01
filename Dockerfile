FROM python:2.7

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && \
    apt-get install -y \
        pkg-config libfreetype6-dev \
        mafft && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app/

COPY requirements.txt /usr/src/app/

RUN pip install supervisor
RUN pip install -r requirements.txt

COPY supervisord.conf /etc/supervisor/conf.d/cron.conf

RUN mkdir -p /etc/cron.d/
RUN ln -s /usr/src/app/config/crontab /etc/cron.d/aggregation
RUN ln -s /usr/src/app /app

COPY . /usr/src/app/

EXPOSE 5000

ENTRYPOINT ["/usr/src/app/start.sh"]
