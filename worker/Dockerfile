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
RUN find ./binwalk -type f | xargs sed -i  's/cramfsprogs//g'
RUN (cd binwalk && echo "y" | ./deps.sh)
RUN (cd binwalk && python setup.py install)

RUN git clone https://github.com/devttys0/sasquatch
RUN find ./sasquatch -type f | xargs sed -i  's/-Werror//g'
RUN (cd sasquatch && ./build.sh)

## ADD ADDITIONAL UTILITIES HERE ##

RUN apt-get install php -y

# useful for debugging

RUN apt-get install vim -y

# configure server files

ENV USER worker

RUN useradd $USER
RUN mkdir /home/$USER
WORKDIR /home/$USER
RUN chown $USER /home/$USER

# USER $USER

COPY --chown=worker analysis  ./analysis
COPY --chown=worker server.py .

# run server

# test

#COPY firmware2.bin ./analysis/firmware.bin

CMD ["python2", "./server.py"]
