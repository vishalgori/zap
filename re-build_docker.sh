#!/bin/bash
#echo "Enter AWS_ACCESS_KEY_ID:"
#read ID
#echo "Enter AWS_ACCESS_SECRET_KEY:"
#read KEY
echo "================================================================================"
echo "Checking if old containers exist locally."
#if [ -z "$(docker ps --no-trunc -aq)" ]; then echo "No old containers exist"; else echo "Deleting old containers"; docker rm -f `docker ps --no-trunc -aq`; fi
if [ -z "$(docker ps -a |grep zapauth)" ]; then echo "Old zapauth container doesn't exist";else echo "Deleting old zapauth container.";docker rm -f zapauth; fi
echo ""
echo ""
echo "================================================================================"
echo "Building latest zapauth docker image."
#docker build --no-cache -t zapauth:latest .
docker build -t zapauth:latest .
echo ""
echo ""
echo "================================================================================"
echo "Deleting old images and keeping only the latest ones in use."
if [ -z "$(docker images -a | grep "^<none>" | awk '{print $3}')" ]; then echo "No old images exist"; else echo "Deleting old images"; docker rmi $(docker images -a | grep "^<none>" | awk '{print $3}'); fi
echo ""
echo ""
echo "================================================================================"
echo "Starting zapauth docker now."
echo ""
echo ""
echo "================================================================================"
#docker run -p 8080:8080 -it -e AWS_ACCESS_KEY_ID=$ID -e AWS_SECRET_ACCESS_KEY=$KEY --name zapauth zapauth /bin/bash -c '/home/zap/app_sec_scan/run.sh >> /home/zap/run.log'
#docker run -p 8000:8000 -it --name defectdojo defectdojo
#docker run --net=host -p 8080:8080 -it -e AWS_ACCESS_KEY_ID=$ID -e AWS_SECRET_ACCESS_KEY=$KEY --name zapauth zapauth
