FROM debian:testing

RUN apt-get update -y

# basic utils

RUN apt-get install binutils apt-utils python python-pip git -y
RUN apt-get install wget gnupg2 -y

# server dependencies

RUN apt-get install python python-pip -y
RUN pip install pika

# binwalk

RUN apt-get install python-lzma
RUN git clone https://github.com/ReFirmLabs/binwalk
RUN cd binwalk && python setup.py install

## ADD ADDITIONAL UTILITIES HERE ##

# configure server files

RUN useradd worker
RUN mkdir /home/worker
WORKDIR /home/worker

COPY analysis .
COPY server.py .

# run server

CMD ["python2", "./server.py"]
