# Customized OWASP ZAP Dockerfile with support for authentication

FROM owasp/zap2docker-stable
MAINTAINER Vishal Gori <vishal.gori@cengage.com>

WORKDIR /home/zap

USER root
# Required for running headless webdriver
RUN apt-get install xvfb && \
		apt-get install git-all -y && \
		pip install pyvirtualdisplay && \
		pip install boto3 && \
		pip install pyyaml && \
		pip install defectdojo_api && \
		pip install s3cmd

RUN apt-get -y remove firefox && \
  	cd /opt && \
		wget http://ftp.mozilla.org/pub/firefox/releases/45.0/linux-x86_64/en-US/firefox-45.0.tar.bz2 && \
		bunzip2 firefox-45.0.tar.bz2 && \
		tar xvf firefox-45.0.tar && \
		ln -s /opt/firefox/firefox /usr/bin/firefox

RUN pip install selenium==2.53.6

USER zap
ADD app_sec_scan /home/zap/app_sec_scan

USER root
RUN chown -R zap:zap /home/zap/*
RUN chmod +x /home/zap/app_sec_scan/run.sh

USER zap
