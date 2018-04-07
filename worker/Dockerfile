FROM debian:testing

RUN apt-get update -y

# basic utils

RUN apt-get install binutils apt-utils python python-pip git -y
RUN apt-get install sudo wget gnupg2 -y

# server dependencies

RUN apt-get install python python-pip -y
RUN pip install pika

# binwalk

RUN git clone https://github.com/ReFirmLabs/binwalk
RUN find ./binwalk -type f | xargs sed -i  's/cramfsprogs //g'
RUN (cd binwalk && echo "y" | ./deps.sh)
RUN (cd binwalk && python setup.py install)

## ADD ADDITIONAL UTILITIES HERE ##

RUN apt-get install php -y

# configure server files

RUN useradd worker
RUN mkdir /home/worker
WORKDIR /home/worker
RUN chown worker /home/worker
USER worker

COPY analysis  ./analysis
COPY server.py .

# run server

# test

# COPY firmware.bin .

CMD ["python2", "./server.py"]
