FROM python:2.7-onbuild

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && \
    apt-get install -y \
        mafft && \
    rm -rf /var/lib/apt/lists/*

RUN pip install supervisor

COPY supervisord.conf /etc/supervisor/conf.d/cron.conf

RUN mkdir -p /etc/cron.d/
RUN ln -s /usr/src/app/config/crontab /etc/cron.d/aggregation
RUN ln -s /usr/src/app /app

EXPOSE 5000

ENTRYPOINT ["/usr/src/app/start.sh"]
